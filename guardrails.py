from agents import Guardrail

class FinanceGuardrail(Guardrail):
    """Validate financial transactions for compliance"""
    async def check(self, input_text):
        # Check for suspicious patterns in financial requests
        red_flags = ["transfer all", "maximum amount", "bypass approval", "override limit"]
        if any(flag in input_text.lower() for flag in red_flags):
            return False, "Potentially suspicious financial request detected"
        return True, None

class HRGuardrail(Guardrail):
    """Validate HR data access for privacy compliance"""
    async def check(self, input_text):
        # Check for sensitive information requests
        sensitive_terms = ["salary", "personal", "ssn", "social security", "health", "medical"]
        if any(term in input_text.lower() for term in sensitive_terms):
            return False, "Request may involve sensitive personal information, requires additional authorization"
        return True, None

class SecurityGuardrail(Guardrail):
    """General security guardrail for all agents"""
    async def check(self, input_text):
        # Check for security-related issues
        security_flags = ["admin access", "override security", "full access", "system privileges"]
        if any(flag in input_text.lower() for flag in security_flags):
            return False, "Request may involve security-sensitive operations"
        return True, None 