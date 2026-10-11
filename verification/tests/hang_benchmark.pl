:- module(arc_benchmark_2, [
    arc2_induce_rule/2,
    arc2_transform/3,
    arc2_induce_recolor/2,
    arc2_recolor_grid/3
]).

arc2_induce_rule(_TrainingPairs, hang).
arc2_transform(hang, _Grid, _Result) :-
    sleep(1.0).

arc2_induce_recolor(_, _) :- fail.
arc2_recolor_grid(_, _, _) :- fail.
