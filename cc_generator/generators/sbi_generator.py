"""SBI Card specific statement generator"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generators.base_generator import BaseStatementGenerator

class SBIGenerator(BaseStatementGenerator):
    def __init__(self, data_file):
        super().__init__('sbi', data_file)
