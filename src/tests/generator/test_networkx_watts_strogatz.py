import os


def test_create():
    import subprocess

    for n in range(100, 2001, 100):
        node_number = n
        neighbor_number = 3
        rewiring_prob = 0.5

        tmpdir = os.path.join(
            "data", "graph", "watts_strogatz", f"neighbor_{neighbor_number}"
        )
        output = os.path.join(tmpdir, f"node_{n:0>4}.json")
        os.makedirs(tmpdir, exist_ok=True)

        dirname = os.path.dirname(output)
        basename = os.path.basename(output)

        command = [
            "python",
            "/home/iharuki/school/itohal/IPSep-CoLa/src/script/generator/networkx_watts_strogatz.py",
            output,
            "--node-number",
            str(node_number),
            "--neighbor-number",
            str(neighbor_number),
            "--rewiring-prob",
            str(rewiring_prob),
        ]
        subprocess.run(command)
        # command = [
        #     "python",
        #     "/home/iharuki/school/itohal/IPSep-CoLa/scripts/draw.py",
        #     output,
        #     "--dest",
        #     os.path.join(dirname, "drawing"),
        # ]
        # subprocess.run(command)
        # command = [
        #     "python",
        #     "/home/iharuki/school/itohal/IPSep-CoLa/scripts/plot.py",
        #     output,
        #     os.path.join(dirname, "drawing", basename),
        #     os.path.join(dirname, "plot.png"),
        # ]
        # subprocess.run(command)


if __name__ == "__main__":
    # unittest.main()
    test_create()
