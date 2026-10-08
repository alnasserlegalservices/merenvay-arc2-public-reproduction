:- initialization(main, main).

main :-
    current_prolog_flag(argv, Argv),
    ( Argv = [TasksFile, BenchmarkFile | _] -> true
    ; format(user_error, 'Usage: swipl run_native_benchmark.pl TASKS BENCHMARK~n', []), halt(2)
    ),
    consult(TasksFile),
    consult(BenchmarkFile),
    get_time(Start),
    arc_benchmark_2:arc2_benchmark_run(Score, Total, Results),
    get_time(End),
    ElapsedMs is round((End-Start)*1000),
    findall(Id, member(result(Id, fail), Results), Fails),
    format('RESULT score=~w total=~w elapsed_ms=~w~n', [Score, Total, ElapsedMs]),
    format('FAILS '), write_term(Fails, [quoted(true)]), nl,
    halt(0).
