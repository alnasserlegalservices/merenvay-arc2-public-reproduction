:- module(arc_benchmark_2, [
    arc2_induce_rule/2,
    arc2_transform/3
]).

arc2_induce_rule(TrainingPairs, reverse_rows) :-
    forall(member(pair(In, Out), TrainingPairs),
           arc2_transform(reverse_rows, In, Out)).

arc2_transform(reverse_rows, Grid, Result) :-
    maplist(reverse, Grid, Result).

arc2_induce_recolor(_, _) :- fail.
arc2_recolor_grid(_, _, _) :- fail.
