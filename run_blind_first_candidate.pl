/* MERENVAY blinded first-candidate diagnostic.
   This is a falsification experiment, not a certified score, not a replacement
   for the upstream benchmark, and not a measure of hidden-set generalisation.

   Crucial separation: first_proposed_output/4 is never passed Expected.
   Exactly one answer-independent candidate is committed BEFORE scoring.
   This experiment tests a deterministic first-candidate selection baseline;
   it does not claim that this heuristic is the best general-purpose solver.
*/
:- initialization(main, main).
:- use_module(library(lists)).

main :-
    current_prolog_flag(argv, Args),
    ( Args = [TasksFile, BenchmarkFile | _] -> true
    ; format(user_error, 'Usage: swipl -q -f run_blind_first_candidate.pl -- TASKS BENCHMARK~n', []),
      halt(2)
    ),
    consult(TasksFile),
    consult(BenchmarkFile),
    findall(task(Id, TrainingPairs, TestIn, Expected),
            arc_tasks_2:arc2_task(Id, TrainingPairs, TestIn, Expected),
            Tasks),
    length(Tasks, Total),
    ( Total =:= 120 -> true
    ; format(user_error, 'Dataset count mismatch: expected 120 public tasks, got ~d~n', [Total]),
      halt(3)
    ),
    get_time(Start),
    maplist(score_one, Tasks, Results),
    get_time(End),
    ElapsedMs is round((End - Start) * 1000),
    findall(Id, member(result(Id, pass(_)), Results), Passed),
    length(Passed, Score),
    findall(Id, member(result(Id, fail(_)), Results), FailIds),
    format('BLIND_FIRST_CANDIDATE score=~d total=~d elapsed_ms=~d~n',
           [Score, Total, ElapsedMs]),
    format('BLIND_FIRST_CANDIDATE_FAILURE_IDS '),
    write_term(FailIds, [quoted(true)]), nl,
    format('SCOPE public-evaluation; answer withheld during candidate selection; upstream task exposure remains~n', []),
    halt(0).

score_one(task(Id, TrainingPairs, TestIn, Expected), result(Id, Status)) :-
    ( catch(
        ( call_with_time_limit(10.0,
              once(first_proposed_output(TrainingPairs, TestIn, Rule, Proposed)))
          -> Outcome = prediction(Rule, Proposed)
          ;  Outcome = no_prediction
        ),
        Error, Outcome = exception(Error)
      ) -> true
    ; Outcome = exception(unexpected_predicate_failure)
    ),
    grade(Outcome, Expected, Status),
    format('BLIND_TASK ~w ~w~n', [Id, Status]).

/* The predicted output is finalised here without an expected answer.
   Unlike the upstream scoring loop, no failed candidate is retried based on
   comparison against the held-out test output. */
first_proposed_output(TrainingPairs, TestIn, Rule, Prediction) :-
    arc_benchmark_2:arc2_induce_rule(TrainingPairs, Rule),
    Rule \== recolor_auto,
    arc_benchmark_2:arc2_transform(Rule, TestIn, Prediction).
first_proposed_output(TrainingPairs, TestIn, recolor_auto, Prediction) :-
    arc_benchmark_2:arc2_induce_recolor(TrainingPairs, Mapping),
    arc_benchmark_2:arc2_recolor_grid(Mapping, TestIn, Prediction).

/* Strict equality, never unification: ground prevents unresolved variables
   from being counted as correct predictions. */
grade(prediction(Rule, Proposed), Expected, pass(Rule)) :-
    ground(Proposed),
    Proposed == Expected, !.
grade(prediction(Rule, _), _, fail(wrong_first_candidate(Rule))) :- !.
grade(no_prediction, _, fail(no_prediction)) :- !.
grade(exception(time_limit_exceeded), _, fail(timeout)) :- !.
grade(exception(Error), _, fail(error(Error))).
