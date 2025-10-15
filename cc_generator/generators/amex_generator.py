"""American Express specific statement generator"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from generators.base_generator import BaseStatementGenerator

class AmexGenerator(BaseStatementGenerator):
    def __init__(self, data_file):
        super().__init__('amex', data_file)
