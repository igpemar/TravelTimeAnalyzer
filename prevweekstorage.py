if Current_Week != prev_week and REQ_SEND == 1:
    This_Week_1 = np.column_stack(
        (w_req_n_1, w_dt_str, w_1_dist_1, w_1_d_avg_1, w_1_d_i_t_1)
    )
    This_Week_2 = np.column_stack(
        (w_req_n_1, w_dt_str, w_2_dist_2, w_2_d_avg_2, w_2_d_i_t_2)
    )

    np.savetxt(
        "Week_" + f"{prev_week:02}" + "_Output_1.csv",
        This_Week_1,
        fmt="%s",
        delimiter=" ; ",
        comments="",
        header="Req nbr. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
    )
    np.savetxt(
        "Week_" + f"{prev_week:02}" + "_Output_2.csv",
        This_Week_1,
        fmt="%s",
        delimiter=" ; ",
        comments="",
        header="Req nbr. ; Timestamp ; Distance [km] ; Duration (incl.traffic) [min] ; Duration (excl.traffic) [min]",
    )
    prev_week = Current_Week
    (
        w_req_n_1,
        w_dt_str,
        w_1_d_i_t_1,
        w_2_d_i_t_2,
        w_1_d_avg_1,
        w_2_d_avg_2,
        w_1_dist_1,
        w_2_dist_2,
    ) = ([], [], [], [], [], [], [], [])
