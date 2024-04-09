import jax

jax.config.update("jax_enable_x64", True)
jax.config.update("jax_platform_name", "cpu")

import jax.numpy as jnp
import numpy as np
from jax import jit

import jaxley as jx


def test_move_cell():
    nseg = 4

    # Test move on a cell with compute_xyz()
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell(branch, parents=[-1, 0, 0, 1, 1])
    cell.compute_xyz()
    cell.move(20.0, 30.0, 5.0)
    assert cell.xyzr[0][0, 0] == 20.0
    assert cell.xyzr[0][0, 1] == 30.0
    assert cell.xyzr[0][0, 2] == 5.0

    # Test move_to on a cell that starts with a specified xyzr
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell(
        branch,
        parents=[-1],
        xyzr=[
            np.array(
                [
                    [5.0, 10.0, 1.0, 10.0],
                    [10.0, 15.0, 0.0, 10.0],
                ]
            )
        ],
    )
    cell.move(6.0, 9.0, 3.0)
    assert cell.xyzr[0][0, 0] == 11.0
    assert cell.xyzr[0][0, 1] == 19.0
    assert cell.xyzr[0][0, 2] == 4.0
    assert cell.xyzr[0][0, 3] == 10.0


def test_move_network():
    nseg = 2
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell([branch, branch, branch], parents=[-1, 0, 0])
    cell.compute_xyz()
    net = jx.Network([cell, cell, cell])
    net.move(20.0, 30.0, 5.0)
    for i in [0, 3, 6]:
        assert net.xyzr[i][0, 0] == 20.0
        assert net.xyzr[i][0, 1] == 30.0
        assert net.xyzr[i][0, 2] == 5.0


def test_move_to_cell():
    nseg = 4
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell(branch, parents=[-1, 0, 0, 1, 1])
    cell.compute_xyz()
    cell.move_to(20.0, 30.0, 5.0)
    assert cell.xyzr[0][0, 0] == 20.0
    assert cell.xyzr[0][0, 1] == 30.0
    assert cell.xyzr[0][0, 2] == 5.0

    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell(
        branch,
        parents=[-1],
        xyzr=[
            np.array(
                [
                    [5.0, 10.0, 1.0, 10.0],
                    [10.0, 15.0, 0.0, 10.0],
                ]
            )
        ],
    )
    cell.move_to(6.0, 9.0, 3.0)
    assert cell.xyzr[0][0, 0] == 6.0
    assert cell.xyzr[0][0, 1] == 9.0
    assert cell.xyzr[0][0, 2] == 3.0
    assert cell.xyzr[0][0, 3] == 10.0


def test_move_to_network():
    nseg = 4
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell([branch, branch, branch], parents=[-1, 0, 0])
    cell.compute_xyz()
    net = jx.Network([cell, cell, cell])
    net.move_to(10.0, 20.0, 30.0)
    # Branch 0 of cell 0
    assert net.xyzr[0][0, 0] == 10.0
    assert net.xyzr[0][0, 1] == 20.0
    assert net.xyzr[0][0, 2] == 30.0
    # Branch 0 of cell 1
    assert net.xyzr[3][0, 0] == 10.0
    assert net.xyzr[3][0, 1] == 20.0
    assert net.xyzr[3][0, 2] == 30.0


def test_move_to_arrays():
    """Test with network"""
    nseg = 4
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=nseg)
    cell = jx.Cell([branch, branch, branch], parents=[-1, 0, 0])
    cell.compute_xyz()
    net = jx.Network([cell, cell, cell])
    x_coords = np.array([10.0, 20.0, 30.0])
    y_coords = np.array([5.0, 15.0, 25.0])
    z_coords = np.array([1.0, 2.0, 3.0])
    net.move_to(x_coords, y_coords, z_coords)
    assert net.xyzr[0][0, 0] == 10.0
    assert net.xyzr[0][1, 0] == nseg * 10.0 + 10.0
    assert net.xyzr[0][0, 1] == 5.0
    assert net.xyzr[0][0, 2] == 1.0
    assert net.xyzr[3][0, 0] == 20.0
    assert net.xyzr[3][0, 2] == 2.0
    assert net.xyzr[6][0, 1] == 25.0


def test_move_to_cellview():
    comp = jx.Compartment()
    branch = jx.Branch(comp, nseg=2)
    cell = jx.Cell([branch, branch, branch], parents=[-1, 0, 0])
    cell.compute_xyz()
    net = jx.Network([cell for _ in range(3)])

    # Test with float input
    net.cell(0).move_to(50.0, 3.0, 40.0)
    assert net.xyzr[0][0, 0] == 50.0
    assert net.xyzr[0][0, 1] == 3.0
    assert net.xyzr[0][0, 2] == 40.0

    # Test with array input
    net = jx.Network([cell for _ in range(4)])
    testx = np.array([1.0, 2.0, 3.0])
    testy = np.array([4.0, 5.0, 6.0])
    testz = np.array([7.0, 8.0, 9.0])
    net.cell([0, 1, 2]).move_to(testx, testy, testz)
    assert net.xyzr[0][0, 0] == 1.0
    assert net.xyzr[3][0, 1] == 5.0
    assert net.xyzr[6][0, 2] == 9.0
    assert net.xyzr[9][0, 0] == 0.0
