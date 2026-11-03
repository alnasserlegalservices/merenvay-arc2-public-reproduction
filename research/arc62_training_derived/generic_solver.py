"""MERENVAY independent, from-demonstrations-only symbolic ARC baseline.

No task IDs, public challenge answer keys, Mentova recipe files, language models,
external solvers, private project files or private knowledge are used in inference.
This intentionally supports a *limited* grammar. It is not a trained universal
ARC solver, a verified Kaggle entry, or the private legal Decision DNA engine.

The algorithm proposes reusable grid transformations, optionally fits an
example-consistent color mapping, checks *all* visible training pairs, and
produces at most two grids. A scored hidden output is never accessible here.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any

MAX_SIDE=30
D4=("identity","rot90","rot180","rot270","flip_h","flip_v","transpose","anti_diag")
SHAPES=("crop_nonzero","scale2","scale3","tile2x2")

Grid=tuple[tuple[int,...],...]

def validate_grid(grid:Any)->Grid:
    if type(grid) not in (list,tuple) or not 1<=len(grid)<=MAX_SIDE:
        raise ValueError("ARC grid must have 1..30 rows")
    width=None
    rows=[]
    for row in grid:
        if type(row) not in (tuple,list) or not row or len(row)>MAX_SIDE:
            raise ValueError("ARC grid must have 1..30 columns")
        if width is None:width=len(row)
        if len(row)!=width or any(type(c) is not int or not 0<=c<=9 for c in row):
            raise ValueError("ARC grid must be rectangular, integer colors 0..9")
        rows.append(tuple(row))
    return tuple(rows)


def as_list(grid:Grid)->list[list[int]]:
    return [list(row) for row in grid]


def _operation(g:Grid,op:str)->Grid:
    h,w=len(g),len(g[0])
    if op=='identity':return g
    if op=='rot90':return tuple(tuple(g[h-1-r][c] for r in range(h)) for c in range(w))
    if op=='rot180':return tuple(tuple(reversed(row)) for row in reversed(g))
    if op=='rot270':return tuple(tuple(g[r][w-c-1] for r in range(h)) for c in range(w))
    if op=='flip_h':return tuple(tuple(reversed(row)) for row in g)
    if op=='flip_v':return tuple(reversed(g))
    if op=='transpose':return tuple(tuple(g[r][c] for r in range(h)) for c in range(w))
    if op=='anti_diag':return tuple(tuple(g[h-r-1][w-c-1] for r in range(h)) for c in range(w))
    if op=='crop_nonzero':
        pts=[(r,c) for r,row in enumerate(g) for c,v in enumerate(row) if v!=0]
        if not pts:raise ValueError("Foreground crop undefined on empty foreground")
        r0=min(p[0] for p in pts);r1=max(p[0] for p in pts)
        c0=min(p[1] for p in pts);c1=max(p[1] for p in pts)
        return tuple(tuple(g[r][c] for c in range(c0,c1+1)) for r in range(r0,r1+1))
    if op.startswith('scale'):
        k=int(op[5:])
        if k not in (2,3) or h*k>MAX_SIDE or w*k>MAX_SIDE:
            raise ValueError("Scale would exceed ARC bounds")
        return tuple(tuple(g[r//k][c//k] for c in range(w*k)) for r in range(h*k))
    if op=='tile2x2':
        if h*2>MAX_SIDE or w*2>MAX_SIDE:raise ValueError("Tile would exceed ARC bounds")
        return tuple(tuple(g[r%h][c%w] for c in range(w*2)) for r in range(h*2))
    raise ValueError("Unsupported operator")


@dataclass(frozen=True)
class Program:
    ops:tuple[str,...]
    mapping:tuple[tuple[int,int],...]=()

    @property
    def name(self)->str:
        s='+'.join(self.ops) if self.ops else 'identity'
        return s + ('|color_map' if self.mapping else '')

    @property
    def cost(self)->int:
        return len(self.ops)*2+int(bool(self.mapping))

    def structure(self,g:Grid)->Grid:
        for op in self.ops:g=_operation(g,op)
        return g

    def apply(self,g:Grid)->Grid:
        g=self.structure(g)
        if self.mapping:
            m=dict(self.mapping)
            g=tuple(tuple(m.get(v,v) for v in row) for row in g)
        return validate_grid(g)


def transform(grid:Any, steps:tuple[str,...], mapping:tuple[tuple[int,int],...]=())->list[list[int]]:
    return as_list(Program(tuple(steps),mapping).apply(validate_grid(grid)))


def _candidate_shapes():
    """Reusable grammar; no direct ports or constants tied to known task IDs."""
    yield Program(())
    for op in D4[1:]:yield Program((op,))
    for shape in SHAPES:
        yield Program((shape,))
    # Two-step structural composition from the same universal grammar.
    for shape in SHAPES:
        for geom in D4[1:]:
            yield Program((shape,geom))
            yield Program((geom,shape))
    for first in SHAPES:
        for second in SHAPES:
            if first!=second:yield Program((first,second))


def _fit_map(p:Program,demos:list[tuple[Grid,Grid]]):
    mapping={}
    for a,b in demos:
        try:s=p.structure(a)
        except ValueError:return None
        if len(s)!=len(b) or len(s[0])!=len(b[0]):return None
        for srow,brow in zip(s,b):
            for x,y in zip(srow,brow):
                if x in mapping and mapping[x]!=y:return None
                mapping[x]=y
    if all(x==y for x,y in mapping.items()):return None
    return tuple(sorted(mapping.items()))


def _validated_demos(train:list[dict])->list[tuple[Grid,Grid]]:
    if type(train) is not list or not train:raise ValueError('Nonempty train list required')
    result=[]
    for pair in train:
        if type(pair) is not dict or set(pair)!={'input','output'}:
            raise ValueError('Training pairs must contain only input and output')
        result.append((validate_grid(pair['input']),validate_grid(pair['output'])))
    return result


def fit_programs(train:list[dict],max_candidates:int=256,max_checks:int=512):
    demos=_validated_demos(train)
    if type(max_candidates) is not int or max_candidates<1 or max_candidates>512:
        raise ValueError('candidate limit out of range')
    if type(max_checks) is not int or max_checks<1 or max_checks>1024:
        raise ValueError('demo-check limit out of range')
    accepted=[];witnesses=[];seen=set();examined=0;checks=0
    for prototype in _candidate_shapes():
        branches=[prototype]
        remap=_fit_map(prototype,demos)
        if remap:branches.append(Program(prototype.ops,remap))
        for p in branches:
            if examined>=max_candidates or checks>=max_checks:break
            if p.name in seen:continue
            seen.add(p.name);examined+=1
            fit=True
            for j,(a,b) in enumerate(demos):
                if checks>=max_checks:fit=False;break
                checks+=1
                try:out=p.apply(a)
                except ValueError:out=()
                if out!=b:
                    fit=False
                    if len(witnesses)<20:
                        witnesses.append({'program':p.name,'demonstration_index':j,
                                          'failure_kind':'shape_or_color_mismatch'})
                    break
            if fit:accepted.append(p)
        if examined>=max_candidates or checks>=max_checks:break
    accepted.sort(key=lambda p:(p.cost,p.name))
    return accepted,{'programs_evaluated':examined,'demonstrations_checked':checks,
                     'supported_count':len(accepted),'first_failure_witnesses':witnesses,
                     'source':'visible training demonstrations only',
                     'hidden_accuracy':'NOT_MEASURED'}


def program_trace(train:list[dict])->dict:
    return fit_programs(train)[1]


def solve_task(train:list[dict],test_inputs:list[Any],max_candidates:int=256):
    programs,_=fit_programs(train,max_candidates=max_candidates)
    if type(test_inputs) is not list or not test_inputs:raise ValueError('Test input list required')
    tests=[validate_grid(x) for x in test_inputs]
    results=[]
    for g in tests:
        selected=[]
        for p in programs:
            try:res=p.apply(g)
            except ValueError:continue
            if res not in selected:selected.append(res)
            if len(selected)==2:break
        if not selected:selected=[g]  # Explicitly unverified fallback, never claim success.
        a=as_list(selected[0]);b=as_list(selected[1] if len(selected)>1 else selected[0])
        results.append({'attempt_1':a,'attempt_2':b})
    return results


def solve_challenges(challenges:dict[str,dict])->dict[str,list[dict]]:
    if type(challenges) is not dict or not challenges:
        raise ValueError('Expected nonempty ARC challenge JSON object')
    results={}
    for id,task in challenges.items():
        # IDs are output record keys only; never inspected by hypothesis generator.
        if type(id) is not str or not id or type(task) is not dict or set(task)!={'train','test'}:
            raise ValueError('Invalid ARC task schema')
        tests=task['test']
        if type(tests) is not list or not tests or any(type(t) is not dict or set(t)!={'input'} for t in tests):
            raise ValueError('Only label-free test inputs are accepted in inference')
        results[id]=solve_task(task['train'],[v['input'] for v in tests])
    return results


def main():
    parser=argparse.ArgumentParser(description='Training-only rule induction; exploratory baseline')
    parser.add_argument('--challenges',type=Path,required=True)
    parser.add_argument('--submission',type=Path,required=True)
    args=parser.parse_args()
    tasks=json.loads(args.challenges.read_text(encoding='utf-8'))
    rows=solve_challenges(tasks)
    args.submission.write_text(json.dumps(rows,sort_keys=True,separators=(',',':'))+'\n',encoding='utf-8')
    print('WROTE',len(rows),'tasks, answer labels unavailable; no score claimed')


if __name__=='__main__':main()
