import time
from typing import Dict, Optional
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 5, window_minutes: int = 60):
        """
        Initialize rate limiter
        
        Args:
            max_requests: Maximum number of requests per window
            window_minutes: Time window in minutes
        """
        self.max_requests = max_requests
        self.window_minutes = window_minutes
        self.requests: Dict[str, list] = {}
        self.blocked_ips: Dict[str, datetime] = {}
        
    def allow_request(self, ip_address: str) -> bool:
        """
        Check if request is allowed for given IP address
        """
        now = datetime.now()
        
        # Check if IP is temporarily blocked
        if ip_address in self.blocked_ips:
            if now < self.blocked_ips[ip_address]:
                return False
            else:
                # Unblock IP
                del self.blocked_ips[ip_address]
        
        # Clean old requests
        self._clean_old_requests(ip_address, now)
        
        # Get current requests for this IP
        if ip_address not in self.requests:
            self.requests[ip_address] = []
        
        current_requests = self.requests[ip_address]
        
        # Check if limit exceeded
        if len(current_requests) >= self.max_requests:
            # Block IP for extended period
            self.blocked_ips[ip_address] = now + timedelta(minutes=self.window_minutes * 2)
            return False
        
        # Add current request
        current_requests.append(now)
        
        return True
    
    def _clean_old_requests(self, ip_address: str, now: datetime) -> None:
        """
        Remove requests older than the time window
        """
        if ip_address not in self.requests:
            return
        
        window_start = now - timedelta(minutes=self.window_minutes)
        self.requests[ip_address] = [
            req_time for req_time in self.requests[ip_address]
            if req_time > window_start
        ]
    
    def get_remaining_requests(self, ip_address: str) -> int:
        """
        Get number of remaining requests for IP
        """
        if ip_address in self.blocked_ips:
            if datetime.now() < self.blocked_ips[ip_address]:
                return 0
            else:
                del self.blocked_ips[ip_address]
        
        self._clean_old_requests(ip_address, datetime.now())
        
        if ip_address not in self.requests:
            return self.max_requests
        
        return max(0, self.max_requests - len(self.requests[ip_address]))
    
    def get_time_until_reset(self, ip_address: str) -> Optional[int]:
        """
        Get time in seconds until rate limit resets
        """
        if ip_address in self.blocked_ips:
            remaining = self.blocked_ips[ip_address] - datetime.now()
            return max(0, int(remaining.total_seconds()))
        
        if ip_address not in self.requests or not self.requests[ip_address]:
            return None
        
        oldest_request = min(self.requests[ip_address])
        reset_time = oldest_request + timedelta(minutes=self.window_minutes)
        remaining = reset_time - datetime.now()
        
        return max(0, int(remaining.total_seconds()))
    
    def reset_ip(self, ip_address: str) -> None:
        """
        Reset rate limit for specific IP (admin function)
        """
        if ip_address in self.requests:
            del self.requests[ip_address]
        
        if ip_address in self.blocked_ips:
            del self.blocked_ips[ip_address]
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get rate limiter statistics
        """
        now = datetime.now()
        active_ips = 0
        blocked_ips = 0
        total_requests = 0
        
        # Clean old data first
        for ip in list(self.requests.keys()):
            self._clean_old_requests(ip, now)
            if self.requests[ip]:
                active_ips += 1
                total_requests += len(self.requests[ip])
        
        # Count blocked IPs
        for ip, block_time in list(self.blocked_ips.items()):
            if now < block_time:
                blocked_ips += 1
            else:
                del self.blocked_ips[ip]
        
        return {
            'active_ips': active_ips,
            'blocked_ips': blocked_ips,
            'total_requests_in_window': total_requests,
            'max_requests_per_window': self.max_requests,
            'window_minutes': self.window_minutes
        }
    
    def cleanup(self) -> None:
        """
        Clean up old data to prevent memory leaks
        """
        now = datetime.now()
        
        # Clean old requests
        for ip in list(self.requests.keys()):
            self._clean_old_requests(ip, now)
            if not self.requests[ip]:
                del self.requests[ip]
        
        # Clean expired blocks
        for ip in list(self.blocked_ips.keys()):
            if now >= self.blocked_ips[ip]:
                del self.blocked_ips[ip]

# Premium rate limiter with higher limits
class PremiumRateLimiter(RateLimiter):
    def __init__(self):
        super().__init__(max_requests=50, window_minutes=60)  # 50 requests per hour for premium users

# Global rate limiter instances
standard_limiter = RateLimiter(max_requests=5, window_minutes=60)  # 5 requests per hour
premium_limiter = PremiumRateLimiter()  # 50 requests per hour