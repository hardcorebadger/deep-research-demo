class Portfolio:
    # Schema definitions as separate class variables
    ADD_COMPANIES_SCHEMA = {
        "name": "add_companies",
        "description": "Adds a list of companies to the portfolio",
        "input_schema": {
            "type": "object",
            "properties": {
                "companies": {
                    "type": "array",
                    "description": "A list of companies to add to the portfolio (use ticker symbols)"
                },
                "total_weight": {
                    "type": "number",
                    "description": "The total weight within the portfolio (out of 1.00) to be divided evenly amongst the companies added"
                }
            },
            "required": ["companies", "total_weight"]
        }
    }

    REMOVE_COMPANIES_SCHEMA = {
        "name": "remove_companies",
        "description": "Removes a list of companies from the portfolio",
        "input_schema": {
            "type": "object",
            "properties": {
                "companies": {
                    "type": "array",
                    "description": "A list of companies to remove from the portfolio (use ticker symbols)"
                }
            },
            "required": ["companies"]
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

    CHANGE_WEIGHT_SCHEMA = {
        "name": "change_weight",
        "description": "Changes the weight of a company in the portfolio",
        "input_schema": {
            "type": "object",
            "properties": {
                "companies": {
                    "type": "array",
                    "description": "A list of companies to change the weight of (use ticker symbols)"
                },
                "weight": {
                    "type": "number",
                    "description": "The weight to change the companies to (out of 1.00) to be divided evenly amongst the companies"
                }
            },
            "required": ["companies", "weight"]
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
            self.ADD_COMPANIES_SCHEMA,
            self.REMOVE_COMPANIES_SCHEMA,
            self.GET_PORTFOLIO_SCHEMA,
            self.CHANGE_WEIGHT_SCHEMA,
            self.WEIGHT_BY_SCHEMA
        ]
        
        functions = [
            self.add_companies,
            self.remove_companies,
            self.get_portfolio,
            self.change_weight,
            self.weight_by
        ]
        return schemas, functions

    def _print_portfolio(self):
        """Helper method to print and return the current portfolio state."""
        portfolio_str = str(self)
        print(portfolio_str)
        print()  # Add a blank line for readability
        return portfolio_str

    def add_companies(self, input_json):
        """Add companies to portfolio with equal weights."""
        companies = input_json["companies"]
        total_weight = input_json["total_weight"]
        if not companies:
            return "No companies to add"
        weight_per_company = total_weight / len(companies)
        for company in companies:
            self.portfolio[company] = weight_per_company
        return self._print_portfolio()
    
    def remove_companies(self, input_json):
        """Remove companies from portfolio."""
        companies = input_json["companies"]
        for company in companies:
            self.portfolio.pop(company, None)
        return self._print_portfolio()
    
    def get_portfolio(self, input_json=None):
        """Return current portfolio."""
        return self._print_portfolio()
    
    def change_weight(self, input_json):
        """Change weight of specified companies equally."""
        companies = input_json["companies"]
        weight = input_json["weight"]
        if not companies:
            return "No companies to change weight for"
        weight_per_company = weight / len(companies)
        for company in companies:
            if company in self.portfolio:
                self.portfolio[company] = weight_per_company
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
