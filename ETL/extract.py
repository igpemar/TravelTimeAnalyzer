import sys
import pandas


def restart_check():
    while True:
        s = input(
            " Would you like to start from scratch and erase the existing data? Y/N/A "
        )
        req_n_1, req_n_2, dt_str, d_i_t_1, d_i_t_2, d_avg_1, d_avg_2, dist_1, dist_2 = (
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
            [],
        )
        if s == "A" or s == "A":
            sys.exit()
        elif s == "y" or s == "Y":
            Restart_Flag = 1
            return (
                req_n_1,
                req_n_2,
                dt_str,
                d_i_t_1,
                d_i_t_2,
                d_avg_1,
                d_avg_2,
                dist_1,
                dist_2,
                Restart_Flag,
            )
        elif s == "n" or s == "N":
            Restart_Flag = 0
            try:
                Output_1 = pandas.read_csv("Output_1.csv", sep=";")
                Output_2 = pandas.read_csv("Output_2.csv", sep=";")
            except:
                print(
                    " No data files were found, impossible to restart from existing data, exiting ..."
                )
                sys.exit()

            for i in range(Output_1.shape[0]):
                req_n_1.append(Output_1.values[i][0])
                dt_str.append(Output_1.values[i][1].strip())
                dist_1.append(Output_1.values[i][2])
                d_avg_1.append(Output_1.values[i][3])
                d_i_t_1.append(Output_1.values[i][4])

            for i in range(Output_2.shape[0]):
                req_n_2.append(Output_2.values[i][0])
                dist_2.append(Output_2.values[i][2])
                d_avg_2.append(Output_2.values[i][3])
                d_i_t_2.append(Output_2.values[i][4])

            return (
                req_n_1,
                dt_str,
                dist_1,
                d_avg_1,
                d_i_t_1,
                req_n_2,
                dist_2,
                d_avg_2,
                d_i_t_2,
                Restart_Flag,
            )
