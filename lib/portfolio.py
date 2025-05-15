class Portfolio:
    # Schema definitions as separate class variables
    UPDATE_PORTFOLIO_SCHEMA = {
        "name": "update_portfolio",
        "description": "Updates the portfolio by adding companies or changing weights of existing companies",
        "input_schema": {
            "type": "object",
            "properties": {
                "companies": {
                    "type": "object",
                    "description": "An object mapping company ticker symbols to their desired portfolio weights as decimal values"
                },
                "normalize": {
                    "type": "boolean",
                    "description": "Whether to normalize the entire portfolio to 100% after this update",
                    "default": False
                }
            },
            "required": ["companies"]
        }
    }

    REMOVE_COMPANIES_SCHEMA = {
        "name": "remove_companies",
        "description": "Removes companies from the portfolio",
        "input_schema": {
            "type": "object",
            "properties": {
                "tickers": {
                    "type": "array",
                    "description": "A list of company ticker symbols to remove from the portfolio",
                    "items": {
                        "type": "string"
                    }
                },
                "normalize": {
                    "type": "boolean",
                    "description": "Whether to normalize the remaining portfolio to 100% after removal",
                    "default": False
                }
            },
            "required": ["tickers"]
        }
    }

    GET_PORTFOLIO_SCHEMA = {
        "name": "get_portfolio",
        "description": "Returns the current portfolio",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    }

    WEIGHT_BY_SCHEMA = {
        "name": "weight_by",
        "description": "Weights the portfolio by the given metric",
        "input_schema": {
            "type": "object",
            "properties": {
                "metric": {
                    "type": "string",
                    "description": "The metric to weight the portfolio by",
                    "enum": ["market_cap", "revenue", "earnings", "cash_flow", "pe_ratio", "book_value", "dividend_yield", "beta", "volume", "price", "change", "volume_change", "price_change", "change_percent", "volume_change_percent", "price_change_percent"]
                }
            },
            "required": ["metric"]
        }
    }

    def __init__(self):
        self.portfolio = {}  # Dictionary to store {ticker: weight} pairs
    
    def get_schemas_and_functions(self):
        """Returns a tuple of (schemas, functions) where schemas is a list of schema definitions
        and functions is a list of corresponding function references bound to this instance."""
        schemas = [
            self.UPDATE_PORTFOLIO_SCHEMA,
            self.REMOVE_COMPANIES_SCHEMA,
            self.GET_PORTFOLIO_SCHEMA,
            self.WEIGHT_BY_SCHEMA
        ]
        
        functions = [
            self.update_portfolio,
            self.remove_companies,
            self.get_portfolio,
            self.weight_by
        ]
        return schemas, functions

    def _normalize_portfolio(self):
        """Helper method to normalize portfolio weights to sum to 1.0"""
        total_weight = sum(self.portfolio.values())
        if total_weight > 0:
            for ticker in self.portfolio:
                self.portfolio[ticker] /= total_weight

    def _print_portfolio(self):
        """Helper method to print and return the current portfolio state."""
        portfolio_str = str(self)
        print(portfolio_str)
        print()  # Add a blank line for readability
        return portfolio_str

    def update_portfolio(self, input_json):
        """Update portfolio with new companies and weights."""
        companies = input_json["companies"]
        normalize = input_json.get("normalize", False)
        
        # Update portfolio with new weights
        for ticker, weight in companies.items():
            self.portfolio[ticker] = weight
            
        if normalize:
            self._normalize_portfolio()
            
        return self._print_portfolio()
    
    def remove_companies(self, input_json):
        """Remove companies from portfolio."""
        tickers = input_json["tickers"]
        normalize = input_json.get("normalize", False)
        
        for ticker in tickers:
            self.portfolio.pop(ticker, None)
            
        if normalize:
            self._normalize_portfolio()
            
        return self._print_portfolio()
    
    def get_portfolio(self, input_json=None):
        """Return current portfolio."""
        return self._print_portfolio()
    
    def weight_by(self, input_json):
        """Placeholder for weighting by metric - would need actual data implementation."""
        metric = input_json["metric"]
        # This is a placeholder - in reality would need to fetch actual data
        # and calculate weights based on the metric
        pass
        return self._print_portfolio()
    
    def __str__(self):
        """Pretty print the portfolio."""
        if not self.portfolio:
            return "Empty Portfolio"
        
        # Sort by weight descending
        sorted_portfolio = sorted(self.portfolio.items(), key=lambda x: x[1], reverse=True)
        
        # Format as a nice string
        lines = ["Portfolio:"]
        for ticker, weight in sorted_portfolio:
            lines.append(f"  {ticker}: {weight:.2%}")
        
        return "\n".join(lines)
