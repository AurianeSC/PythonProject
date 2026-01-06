import numpy as np
import pandas as pd

"Calculates the correlation matrix between asset returns in order to analyze their dependence"
def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
    return returns.corr()

"Calculates the average annual return of the portfolio based on daily returns"
def annualized_return(port_ret: pd.Series, periods_per_year: int = 252) -> float:
    return float(port_ret.mean() * periods_per_year)

"Calculates annualized volatility, a measure of portfolio risk"
def annualized_volatility(port_ret: pd.Series, periods_per_year: int = 252) -> float:
    return float(port_ret.std() * np.sqrt(periods_per_year))

"Calculates the worst relative loss since a historical high"
def max_drawdown(port_val: pd.Series) -> float:
    dd = port_val / port_val.cummax() - 1.0
    return float(dd.min())
