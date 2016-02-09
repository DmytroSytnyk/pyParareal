import sys
sys.path.append('../src')

from timeslice import timeslice
from integrator import integrator
from impeuler import impeuler
from solution_linear import solution_linear
import unittest
import numpy as np

class TestTimeslice(unittest.TestCase):

  def setUp(self):
    t = np.sort( np.random.rand(2) )
    nsteps_c        = 1+np.random.randint(25)
    nsteps_f        = 1+np.random.randint(125)
    self.int_coarse = impeuler(t[0], t[1], nsteps_c)
    self.int_fine   = impeuler(t[0], t[1], nsteps_f)
    self.ts_default = timeslice(self.int_fine, self.int_coarse, 1e-10, 3)

  # Timeslice can be instantiated
  def test_caninstantiate(self):
    ts = timeslice(self.int_fine, self.int_coarse, 1e-10, 5)

  # Negative tolerance throws exception
  def test_failsnegativetol(self):
    with self.assertRaises(AssertionError):
      ts = timeslice(self.int_fine, self.int_coarse, -1e-5, 5)

  # Non-float tolerance throws exception
  def test_failsintegertol(self):
    with self.assertRaises(AssertionError):
      ts = timeslice(self.int_fine, self.int_coarse, 1, 5)

  # Non-int iter_max raises exception
  def test_failsfloatitermax(self):
    with self.assertRaises(AssertionError):
      ts = timeslice(self.int_fine, self.int_coarse, 1e-10, 2.5)

  # Negative iter_max raises exception
  def test_failsnegativeitermax(self):
    with self.assertRaises(AssertionError):
      ts = timeslice(self.int_fine, self.int_coarse, 1e-10, -5)

  # Different values for tstart in fine and coarse integrator raise exception
  def test_failsdifferenttstart(self):
    int_c = integrator(1e-10+self.int_coarse.tstart, self.int_coarse.tend, self.int_coarse.nsteps)
    with self.assertRaises(AssertionError):
      ts = timeslice(self.int_fine, int_c, 1e-10, 5)

  # Different values for tend in fine and coarse integrator raise exception
  def test_failsdifferenttend(self):
    int_c = integrator(self.int_coarse.tstart, 1e-10+self.int_coarse.tend, self.int_coarse.nsteps)
    with self.assertRaises(AssertionError):
      ts = timeslice(self.int_fine, int_c, 1e-10, 5)   

  # Directly after initialisation, is_converged returns false unless max_iter = 0
  def test_initiallynotconverged(self):
    ts = timeslice(self.int_fine, self.int_coarse, 1e-14+np.random.rand(), 1+np.random.randint(1))
    assert (not ts.is_converged()), "Directly after initialisation, a is_converged should return False"

  # Directly after initialisation, is_converged returns True if max_iter=0
  def test_initiallyconvergedifmaxiterzero(self):
    ts = timeslice(self.int_fine, self.int_coarse, 1e-14+np.random.rand(), 0)
    assert ts.is_converged(), "If max_iter=0, is_converged should return True"
  
  # get_tstart returns correct value
  def test_get_tstart(self):
    assert abs(self.ts_default.get_tstart() - self.int_fine.tstart)==0, "get_start returned wrong value"

  # get_tend returns correct value
  def test_get_tend(self):
    assert abs(self.ts_default.get_tend() - self.int_fine.tend)==0, "get_start returned wrong value"

  # get_sol_fine without running update_fine before throws exception
  def test_getfineexception(self):
    with self.assertRaises(AssertionError):
      sol_fine = self.ts_default.get_sol_fine()

  # get_sol_coarse without running update_coarse before throws exception
  def test_getfineexception(self):
    with self.assertRaises(AssertionError):
      sol_coarse = self.ts_default.get_sol_coarse()

  # set_sol_start with non-solution objects throws exception
  def test_solfinenosolutionthrows(self):
    with self.assertRaises(AssertionError):
      self.ts_default.set_sol_start(-1)

  # get_sol_fine runs
  def test_canrunfine(self):
    ndof = np.random.randint(25)
    A = (-2.0)*np.eye(ndof)
    sol = solution_linear(np.ones(ndof), A)
    self.ts_default.set_sol_start(sol)
    self.ts_default.update_fine()
    sol_ts = self.ts_default.get_sol_fine()
    assert isinstance(sol_ts, solution_linear), "After running update_fine, object returned by get_sol_fine is of wrong type"

  # get_sol_coarse runs
  def test_canruncoarse(self):
    ndof = np.random.randint(25)
    A = (-2.0)*np.eye(ndof)
    sol = solution_linear(np.ones(ndof), A)
    self.ts_default.set_sol_start(sol)
    self.ts_default.update_coarse()
    sol_ts = self.ts_default.get_sol_coarse()
    assert isinstance(sol_ts, solution_linear), "After running update_coarse, object returned by get_sol_coarse is of wrong type"

