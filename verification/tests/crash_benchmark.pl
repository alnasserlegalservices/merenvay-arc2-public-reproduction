:- module(arc_benchmark_2, [
    arc2_induce_rule/2,
    arc2_transform/3,
    arc2_induce_recolor/2,
    arc2_recolor_grid/3
]).

arc2_induce_rule(_TrainingPairs, crash).
arc2_transform(crash, _Grid, _Result) :-
    throw(error(simulated_crash, arc2_transform/3)).

arc2_induce_recolor(_, _) :- fail.
arc2_recolor_grid(_, _, _) :- fail.
