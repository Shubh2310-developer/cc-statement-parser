"""
HDFC Bank specific statement generator
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from generators.base_generator import BaseStatementGenerator

class HDFCGenerator(BaseStatementGenerator):
    """HDFC Bank credit card statement generator"""
    
    def __init__(self, data_file):
        super().__init__('hdfc', data_file)
        
    # Can override specific methods for HDFC-specific customizations
    # For now, using base implementation
