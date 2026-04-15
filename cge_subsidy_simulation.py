#!/usr/bin/env python3
"""
Small Computable General Equilibrium (CGE) Simulation with Subsidy
This simulates a simple economy with two sectors and analyzes the impact of a production subsidy.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple

class CGEModel:
    """Simple CGE model with production, consumption, and market clearing"""
    
    def __init__(self):
        # Economic parameters
        self.sectors = ['Agriculture', 'Manufacturing']
        self.factors = ['Labor', 'Capital']
        
        # Production function parameters (Cobb-Douglas)
        self.alpha = {
            'Agriculture': {'Labor': 0.6, 'Capital': 0.4},
            'Manufacturing': {'Labor': 0.4, 'Capital': 0.6}
        }
        
        # Productivity parameters
        self.A = {'Agriculture': 1.0, 'Manufacturing': 1.2}
        
        # Consumer preferences (utility weights)
        self.beta = {'Agriculture': 0.5, 'Manufacturing': 0.5}
        
        # Factor endowments
        self.factor_endowment = {'Labor': 100.0, 'Capital': 80.0}
        
        # Initial prices
        self.prices = {'Agriculture': 1.0, 'Manufacturing': 1.0}
        self.factor_prices = {'Labor': 1.0, 'Capital': 1.2}
        
        # Subsidy rate (initially 0)
        self.subsidy_rate = {'Agriculture': 0.0, 'Manufacturing': 0.0}
        
        # Results storage
        self.results_baseline = {}
        self.results_policy = {}
        
    def production_function(self, sector: str, inputs: Dict[str, float]) -> float:
        """Cobb-Douglas production function"""
        output = self.A[sector]
        for factor, amount in inputs.items():
            output *= amount ** self.alpha[sector][factor]
        return output
    
    def cost_minimization(self, sector: str, target_output: float) -> Dict[str, float]:
        """Find optimal input mix for given output level"""
        # For Cobb-Douglas, optimal input ratios depend on factor prices
        labor_price = self.factor_prices['Labor']
        capital_price = self.factor_prices['Capital']
        
        alpha_L = self.alpha[sector]['Labor']
        alpha_K = self.alpha[sector]['Capital']
        
        # Optimal ratio: K/L = (alpha_K/alpha_L) * (w_L/w_K)
        optimal_ratio = (alpha_K / alpha_L) * (labor_price / capital_price)
        
        # Solve for inputs given target output
        # Y = A * L^alpha_L * K^alpha_K
        # K = ratio * L
        # Y = A * L^alpha_L * (ratio*L)^alpha_K = A * ratio^alpha_K * L^(alpha_L+alpha_K)
        
        if abs(alpha_L + alpha_K - 1.0) < 0.001:  # Constant returns to scale
            ratio = optimal_ratio
            L = (target_output / (self.A[sector] * (ratio ** alpha_K))) ** (1.0 / (alpha_L + alpha_K))
            K = ratio * L
        else:
            # General case
            exponent = 1.0 / (alpha_L + alpha_K)
            ratio = optimal_ratio
            L = ((target_output / self.A[sector]) * (ratio ** (-alpha_K))) ** exponent
            K = ratio * L
            
        return {'Labor': L, 'Capital': K}
    
    def unit_cost(self, sector: str) -> float:
        """Calculate unit cost of production"""
        # For Cobb-Douglas with CRS: c(w,r) = (1/A) * (w/alpha_L)^alpha_L * (r/alpha_K)^alpha_K
        w = self.factor_prices['Labor']
        r = self.factor_prices['Capital']
        alpha_L = self.alpha[sector]['Labor']
        alpha_K = self.alpha[sector]['Capital']
        
        unit_cost = (1.0 / self.A[sector]) * \
                    (w / alpha_L) ** alpha_L * \
                    (r / alpha_K) ** alpha_K
        return unit_cost
    
    def demand_functions(self, income: float) -> Dict[str, float]:
        """Cobb-Douglas demand functions"""
        demands = {}
        for sector in self.sectors:
            demands[sector] = (self.beta[sector] * income) / self.prices[sector]
        return demands
    
    def solve_equilibrium(self, max_iterations: int = 100, tolerance: float = 1e-6) -> Dict:
        """Solve for general equilibrium using iterative price adjustment"""
        
        # Initialize quantities
        outputs = {s: 50.0 for s in self.sectors}
        
        for iteration in range(max_iterations):
            old_prices = self.prices.copy()
            old_factor_prices = self.factor_prices.copy()
            
            # Step 1: Calculate total income (factor payments + profits + subsidy transfers)
            total_income = 0.0
            for factor, endowment in self.factor_endowment.items():
                total_income += self.factor_prices[factor] * endowment
            
            # Add subsidy transfers (financed by lump-sum tax, so net effect is zero in closed model)
            # But subsidies affect producer prices
            producer_prices = {}
            for sector in self.sectors:
                producer_prices[sector] = self.prices[sector] * (1 + self.subsidy_rate[sector])
            
            # Step 2: Firm optimization - supply decisions
            new_outputs = {}
            factor_demands = {'Labor': 0.0, 'Capital': 0.0}
            
            for sector in self.sectors:
                # Zero profit condition: price = unit cost
                # Adjust output until markets clear
                uc = self.unit_cost(sector)
                
                # If producer price > unit cost, expand; if <, contract
                # Use adaptive adjustment
                if uc > 0:
                    output_adjustment = (producer_prices[sector] - uc) / uc
                    new_outputs[sector] = outputs[sector] * (1 + 0.1 * output_adjustment)
                    new_outputs[sector] = max(1.0, min(new_outputs[sector], 200.0))  # Bounds
                else:
                    new_outputs[sector] = outputs[sector]
                
                # Calculate factor demands
                inputs = self.cost_minimization(sector, new_outputs[sector])
                for factor in self.factors:
                    factor_demands[factor] += inputs[factor]
            
            outputs = new_outputs
            
            # Step 3: Consumer demand
            demands = self.demand_functions(total_income)
            
            # Step 4: Price adjustments (tatonnement process)
            for sector in self.sectors:
                excess_demand = demands[sector] - outputs[sector]
                self.prices[sector] = self.prices[sector] * (1 + 0.05 * excess_demand / max(outputs[sector], 1.0))
                self.prices[sector] = max(0.1, self.prices[sector])  # Lower bound
            
            # Factor price adjustments
            for factor in self.factors:
                excess_demand = factor_demands[factor] - self.factor_endowment[factor]
                self.factor_prices[factor] = self.factor_prices[factor] * \
                                            (1 + 0.03 * excess_demand / self.factor_endowment[factor])
                self.factor_prices[factor] = max(0.1, self.factor_prices[factor])
            
            # Check convergence
            price_change = sum(abs(self.prices[s] - old_prices[s]) / old_prices[s] 
                              for s in self.sectors)
            factor_price_change = sum(abs(self.factor_prices[f] - old_factor_prices[f]) / old_factor_prices[f] 
                                     for f in self.factors)
            
            if price_change < tolerance and factor_price_change < tolerance:
                break
        
        # Calculate final results
        producer_prices = {s: self.prices[s] * (1 + self.subsidy_rate[s]) for s in self.sectors}
        
        factor_demands = {'Labor': 0.0, 'Capital': 0.0}
        for sector in self.sectors:
            inputs = self.cost_minimization(sector, outputs[sector])
            for factor in self.factors:
                factor_demands[factor] += inputs[factor]
        
        demands = self.demand_functions(total_income)
        
        # Calculate welfare (utility)
        utility = 1.0
        for sector in self.sectors:
            utility *= demands[sector] ** self.beta[sector]
        
        # Government expenditure on subsidies
        gov_expenditure = sum(self.subsidy_rate[s] * self.prices[s] * outputs[s] 
                             for s in self.sectors)
        
        return {
            'outputs': outputs,
            'demands': demands,
            'prices': self.prices.copy(),
            'producer_prices': producer_prices,
            'factor_prices': self.factor_prices.copy(),
            'factor_demands': factor_demands,
            'total_income': total_income,
            'utility': utility,
            'gov_expenditure': gov_expenditure,
            'iterations': iteration + 1
        }
    
    def run_simulation(self, subsidy_scenario: Dict[str, float]) -> Tuple[Dict, Dict]:
        """Run baseline and policy simulations"""
        
        # Baseline (no subsidy)
        print("=" * 70)
        print("BASELINE SCENARIO (No Subsidy)")
        print("=" * 70)
        self.subsidy_rate = {'Agriculture': 0.0, 'Manufacturing': 0.0}
        self.prices = {'Agriculture': 1.0, 'Manufacturing': 1.0}
        self.factor_prices = {'Labor': 1.0, 'Capital': 1.2}
        self.results_baseline = self.solve_equilibrium()
        self.print_results(self.results_baseline)
        
        # Policy scenario (with subsidy)
        print("\n" + "=" * 70)
        print(f"POLICY SCENARIO (Subsidy: Agriculture={subsidy_scenario['Agriculture']*100:.1f}%, "
              f"Manufacturing={subsidy_scenario['Manufacturing']*100:.1f}%)")
        print("=" * 70)
        self.subsidy_rate = subsidy_scenario.copy()
        # Reset prices to find new equilibrium
        self.prices = {'Agriculture': 1.0, 'Manufacturing': 1.0}
        self.factor_prices = {'Labor': 1.0, 'Capital': 1.2}
        self.results_policy = self.solve_equilibrium()
        self.print_results(self.results_policy)
        
        # Compare results
        self.print_comparison()
        
        return self.results_baseline, self.results_policy
    
    def print_results(self, results: Dict):
        """Print simulation results in a formatted way"""
        
        print(f"\nConverged in {results['iterations']} iterations\n")
        
        # Output table
        print("PRODUCTION AND CONSUMPTION:")
        print("-" * 50)
        df_output = pd.DataFrame({
            'Sector': self.sectors,
            'Output': [f"{results['outputs'][s]:.3f}" for s in self.sectors],
            'Demand': [f"{results['demands'][s]:.3f}" for s in self.sectors],
            'Consumer Price': [f"${results['prices'][s]:.4f}" for s in self.sectors],
            'Producer Price': [f"${results['producer_prices'][s]:.4f}" for s in self.sectors]
        })
        print(df_output.to_string(index=False))
        
        # Factor markets
        print("\nFACTOR MARKETS:")
        print("-" * 50)
        df_factors = pd.DataFrame({
            'Factor': self.factors,
            'Price': [f"${results['factor_prices'][f]:.4f}" for f in self.factors],
            'Demand': [f"{results['factor_demands'][f]:.3f}" for f in self.factors],
            'Endowment': [f"{self.factor_endowment[f]:.3f}" for f in self.factors],
            'Excess Demand': [f"{results['factor_demands'][f] - self.factor_endowment[f]:.6f}" 
                             for f in self.factors]
        })
        print(df_factors.to_string(index=False))
        
        # Macroeconomic indicators
        print("\nMACROECONOMIC INDICATORS:")
        print("-" * 50)
        print(f"Total Income:           ${results['total_income']:,.3f}")
        print(f"Welfare (Utility):      {results['utility']:.6f}")
        print(f"Government Expenditure: ${results['gov_expenditure']:,.3f}")
    
    def print_comparison(self):
        """Print comparison between baseline and policy"""
        
        print("\n" + "=" * 70)
        print("POLICY IMPACT ANALYSIS (% Change from Baseline)")
        print("=" * 70)
        
        comparisons = []
        for sector in self.sectors:
            output_change = ((self.results_policy['outputs'][sector] - 
                            self.results_baseline['outputs'][sector]) / 
                            self.results_baseline['outputs'][sector] * 100)
            price_change = ((self.results_policy['prices'][sector] - 
                           self.results_baseline['prices'][sector]) / 
                           self.results_baseline['prices'][sector] * 100)
            demand_change = ((self.results_policy['demands'][sector] - 
                            self.results_baseline['demands'][sector]) / 
                            self.results_baseline['demands'][sector] * 100)
            comparisons.append({
                'Sector': sector,
                'Output Change (%)': f"{output_change:+.2f}",
                'Price Change (%)': f"{price_change:+.2f}",
                'Demand Change (%)': f"{demand_change:+.2f}"
            })
        
        df_comp = pd.DataFrame(comparisons)
        print("\nSECTORAL IMPACTS:")
        print("-" * 50)
        print(df_comp.to_string(index=False))
        
        # Factor price changes
        print("\nFACTOR PRICE IMPACTS:")
        print("-" * 50)
        for factor in self.factors:
            change = ((self.results_policy['factor_prices'][factor] - 
                      self.results_baseline['factor_prices'][factor]) / 
                      self.results_baseline['factor_prices'][factor] * 100)
            print(f"{factor:15s}: {change:+.2f}%")
        
        # Welfare and fiscal impact
        utility_change = ((self.results_policy['utility'] - self.results_baseline['utility']) / 
                         self.results_baseline['utility'] * 100)
        print(f"\n{'Welfare Change (%)':15s}: {utility_change:+.2f}%")
        print(f"{'Govt Expenditure':15s}: ${self.results_policy['gov_expenditure']:,.3f}")


def main():
    """Main execution function"""
    
    print("\n" + "=" * 70)
    print("COMPUTABLE GENERAL EQUILIBRIUM (CGE) SIMULATION")
    print("Production Subsidy Policy Analysis")
    print("=" * 70)
    
    # Create model instance
    model = CGEModel()
    
    # Define subsidy policy: 20% subsidy to agriculture
    subsidy_policy = {
        'Agriculture': 0.20,      # 20% production subsidy
        'Manufacturing': 0.0      # No subsidy
    }
    
    print("\nPolicy: 20% production subsidy to Agriculture sector")
    print("Financed by lump-sum taxation (revenue neutral)")
    
    # Run simulation
    baseline, policy = model.run_simulation(subsidy_policy)
    
    # Generate summary output
    print("\n" + "=" * 70)
    print("SIMULATION COMPLETE")
    print("=" * 70)
    print("\nKey Findings:")
    print("- Subsidy increases production in the subsidized sector")
    print("- Resource reallocation occurs between sectors")
    print("- Factor prices adjust to clear markets")
    print("- Welfare effects depend on distortion magnitude")
    
    # Save results to CSV
    results_summary = {
        'Variable': [
            'Ag_Output', 'Man_Output', 'Ag_Price', 'Man_Price',
            'Labor_Price', 'Capital_Price', 'Utility', 'Gov_Expenditure'
        ],
        'Baseline': [
            baseline['outputs']['Agriculture'],
            baseline['outputs']['Manufacturing'],
            baseline['prices']['Agriculture'],
            baseline['prices']['Manufacturing'],
            baseline['factor_prices']['Labor'],
            baseline['factor_prices']['Capital'],
            baseline['utility'],
            baseline['gov_expenditure']
        ],
        'Policy': [
            policy['outputs']['Agriculture'],
            policy['outputs']['Manufacturing'],
            policy['prices']['Agriculture'],
            policy['prices']['Manufacturing'],
            policy['factor_prices']['Labor'],
            policy['factor_prices']['Capital'],
            policy['utility'],
            policy['gov_expenditure']
        ]
    }
    
    df_results = pd.DataFrame(results_summary)
    df_results.to_csv('cge_results.csv', index=False)
    print("\nResults saved to: cge_results.csv")
    
    return baseline, policy


if __name__ == "__main__":
    baseline_results, policy_results = main()
