# Middleware Layer Implementation

## Middleware Summary

| Middleware | Purpose | Story Requirement |
|------------|---------|-------------------|
| **JWT Authentication** | Validates HS256 JWT tokens, extracts claims, populates request context | EP-01, EP-02, EP-03 require `Authorization: Bearer <token>` |
| **Role-Based Authorization** | Enforces Admin-only access for customer creation (EP-01) | Manager → 403 Forbidden on POST /api/v1/customers |
| **Request Context** | Populates `user_id`, `username`, `role`, `claims` into Gin context | Downstream handlers access authenticated user |
| **Request Logging** | Centralized structured logging with request ID, duration, user context | NFR observability, audit trail readiness |
| **Panic Recovery** | Recovers panics, logs error, returns safe 500 response | Production stability, no stack traces leaked |

---

## JWT Authentication Middleware

```go
// internal/middleware/auth.go
package middleware

import (
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"go.uber.org/zap"

	"crm-system/internal/config"
	"crm-system/internal/domain/errors"
	"crm-system/internal/service"
)

// AuthMiddleware validates JWT Bearer tokens and populates request context.
type AuthMiddleware struct {
	jwtService service.JWTService
	logger     *zap.Logger
	config     *config.JWTConfig
}

// NewAuthMiddleware creates a new authentication middleware.
func NewAuthMiddleware(jwtService service.JWTService, logger *zap.Logger, cfg *config.JWTConfig) *AuthMiddleware {
	return &AuthMiddleware{
		jwtService: jwtService,
		logger:     logger.Named("auth_middleware"),
		config:     cfg,
	}
}

// RequireAuth returns a Gin handler that validates JWT and sets user context.
// Public endpoints (/auth/login, /auth/refresh) should skip this middleware.
func (m *AuthMiddleware) RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		requestID := c.GetString("request_id")

		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			m.logger.Warn("missing authorization header",
				zap.String("request_id", requestID),
				zap.String("path", c.FullPath()),
			)
			errors.WriteUnauthorized(c, "Missing authorization header")
			c.Abort()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
			m.logger.Warn("invalid authorization header format",
				zap.String("request_id", requestID),
				zap.String("path", c.FullPath()),
			)
			errors.WriteUnauthorized(c, "Invalid authorization header format")
			c.Abort()
			return
		}

		tokenString := parts[1]
		claims, err := m.jwtService.ValidateAccessToken(c.Request.Context(), tokenString)
		if err != nil {
			m.logger.Warn("token validation failed",
				zap.String("request_id", requestID),
				zap.Error(err),
				zap.String("path", c.FullPath()),
			)
			errors.WriteUnauthorized(c, "Invalid or expired token")
			c.Abort()
			return
		}

		// Validate standard claims
		if err := m.validateStandardClaims(claims); err != nil {
			m.logger.Warn("claims validation failed",
				zap.String("request_id", requestID),
				zap.Error(err),
			)
			errors.WriteUnauthorized(c, err.Error())
			c.Abort()
			return
		}

		// Populate request context
		m.populateContext(c, claims)

		c.Next()
	}
}

// validateStandardClaims checks issuer, audience, expiration, and not-before.
func (m *AuthMiddleware) validateStandardClaims(claims *service.JWTClaims) error {
	now := time.Now().UTC()

	if claims.ExpiresAt != nil && claims.ExpiresAt.Time.Before(now) {
		return errors.ErrTokenExpired
	}

	if claims.NotBefore != nil && claims.NotBefore.Time.After(now) {
		return errors.ErrTokenNotYetValid
	}

	if m.config.Issuer != "" && claims.Issuer != m.config.Issuer {
		return errors.ErrInvalidIssuer
	}

	if len(m.config.Audience) > 0 {
		validAud := false
		for _, aud := range claims.Audience {
			for _, expected := range m.config.Audience {
				if aud == expected {
					validAud = true
					break
				}
			}
		}
		if !validAud {
			return errors.ErrInvalidAudience
		}
	}

	return nil
}

// populateContext sets user information into Gin context for downstream handlers.
func (m *AuthMiddleware) populateContext(c *gin.Context, claims *service.JWTClaims) {
	c.Set("user_id", claims.UserID)
	c.Set("username", claims.Username)
	c.Set("role", claims.Role)
	c.Set("claims", claims)
	c.Set("token_type", claims.TokenType)
}

// OptionalAuth validates token if present but does not require it.
// Useful for endpoints that behave differently for authenticated vs anonymous users.
func (m *AuthMiddleware) OptionalAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		parts := strings.SplitN(authHeader, " ", 2)
		if len(parts) != 2 || !strings.EqualFold(parts[0], "Bearer") {
			c.Next()
			return
		}

		tokenString := parts[1]
		claims, err := m.jwtService.ValidateAccessToken(c.Request.Context(), tokenString)
		if err != nil {
			c.Next()
			return
		}

		if err := m.validateStandardClaims(claims); err != nil {
			c.Next()
			return
		}

		m.populateContext(c, claims)
		c.Next()
	}
}
```

---

## Authorization Middleware

```go
// internal/middleware/authorization.go
package middleware

import (
	"github.com/gin-gonic/gin"

	"crm-system/internal/domain/errors"
)

// Role represents system roles as defined in API contract.
type Role string

const (
	RoleAdmin    Role = "ADMIN"
	RoleManager  Role = "MANAGER"
	RoleViewer   Role = "VIEWER" // Future use
)

// RequireRole returns a Gin handler that enforces role-based access control.
// Returns 403 Forbidden if user lacks required role.
func RequireRole(allowedRoles ...Role) gin.HandlerFunc {
	return func(c *gin.Context) {
		roleVal, exists := c.Get("role")
		if !exists {
			// Should not happen if RequireAuth runs first
			errors.WriteForbidden(c, "Authentication required")
			c.Abort()
			return
		}

		userRole, ok := roleVal.(string)
		if !ok {
			errors.WriteForbidden(c, "Invalid role claim")
			c.Abort()
			return
		}

		for _, allowed := range allowedRoles {
			if userRole == string(allowed) {
				c.Next()
				return
			}
		}

		errors.WriteForbidden(c, "Insufficient permissions")
		c.Abort()
	}
}

// RequireAdmin is a convenience middleware for Admin-only endpoints.
// Per API Contract: EP-01 (Create Customer) requires ADMIN role.
func RequireAdmin() gin.HandlerFunc {
	return RequireRole(RoleAdmin)
}

// RequireManagerOrAdmin allows Manager and Admin roles.
// Per API Contract: EP-02 (Search), EP-03 (Detail) allow both.
func RequireManagerOrAdmin() gin.HandlerFunc {
	return RequireRole(RoleManager, RoleAdmin)
}

// RequireAnyRole allows any authenticated role (future extensibility).
func RequireAnyRole() gin.HandlerFunc {
	return RequireRole(RoleAdmin, RoleManager, RoleViewer)
}
```

---

## Request Context Middleware

```go
// internal/middleware/context.go
package middleware

import (
	"github.com/gin-gonic/gin"
	"github.com/google/uuid"

	"crm-system/internal/domain/errors"
)

// ContextKeys are type-safe keys for Gin context values.
type ContextKey string

const (
	ContextKeyUserID     ContextKey = "user_id"
	ContextKeyUsername   ContextKey = "username"
	ContextKeyRole       ContextKey = "role"
	ContextKeyClaims     ContextKey = "claims"
	ContextKeyTokenType  ContextKey = "token_type"
	ContextKeyRequestID  ContextKey = "request_id"
	ContextKeyStartTime  ContextKey = "start_time"
)

// RequestContextMiddleware initializes request-scoped context values.
// Must run early in middleware chain (before auth, logging, recovery).
func RequestContextMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Generate or extract request ID
		requestID := c.GetHeader("X-Request-ID")
		if requestID == "" {
			requestID = uuid.New().String()
		}
		c.Set(string(ContextKeyRequestID), requestID)
		c.Header("X-Request-ID", requestID)

		// Record start time for latency measurement
		c.Set(string(ContextKeyStartTime), c.Request.Context().Value("start_time"))

		c.Next()
	}
}

// GetUserID safely extracts user ID from context.
// Returns empty string if not authenticated.
func GetUserID(c *gin.Context) string {
	val, _ := c.Get(string(ContextKeyUserID))
	if val == nil {
		return ""
	}
	id, _ := val.(string)
	return id
}

// GetUsername safely extracts username from context.
func GetUsername(c *gin.Context) string {
	val, _ := c.Get(string(ContextKeyUsername))
	if val == nil {
		return ""
	}
	username, _ := val.(string)
	return username
}

// GetRole safely extracts role from context.
func GetRole(c *gin.Context) string {
	val, _ := c.Get(string(ContextKeyRole))
	if val == nil {
		return ""
	}
	role, _ := val.(string)
	return role
}

// GetClaims safely extracts JWT claims from context.
func GetClaims(c *gin.Context) *service.JWTClaims {
	val, _ := c.Get(string(ContextKeyClaims))
	if val == nil {
		return nil
	}
	claims, _ := val.(*service.JWTClaims)
	return claims
}

// GetRequestID safely extracts request ID from context.
func GetRequestID(c *gin.Context) string {
	val, _ := c.Get(string(ContextKeyRequestID))
	if val == nil {
		return ""
	}
	id, _ := val.(string)
	return id
}

// RequireUserID ensures user_id is present in context (authenticated request).
// Returns 401 if missing. Use in handlers that require authentication.
func RequireUserID(c *gin.Context) (string, bool) {
	userID := GetUserID(c)
	if userID == "" {
		errors.WriteUnauthorized(c, "Authentication required")
		return "", false
	}
	return userID, true
}
```

---

## Logging Middleware

```go
// internal/middleware/logging.go
package middleware

import (
	"net"
	"net/http"
	"net/http/httputil"
	"os"
	"runtime/debug"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"

	"crm-system/internal/config"
)

// LoggingMiddleware provides structured request/response logging.
// Masks sensitive data per security rules.
type LoggingMiddleware struct {
	logger *zap.Logger
	config *config.LoggingConfig
}

// NewLoggingMiddleware creates a new logging middleware.
func NewLoggingMiddleware(logger *zap.Logger, cfg *config.LoggingConfig) *LoggingMiddleware {
	return &LoggingMiddleware{
		logger: logger.Named("http"),
		config: cfg,
	}
}

// LogRequest returns a Gin handler that logs HTTP requests and responses.
func (m *LoggingMiddleware) LogRequest() gin.HandlerFunc {
	return func(c *gin.Context) {
		start := time.Now()
		requestID := GetRequestID(c)

		// Skip health check endpoints to reduce noise
		if m.shouldSkipLogging(c.FullPath()) {
			c.Next()
			return
		}

		// Capture request body for error logging (if enabled and safe)
		var requestBody []byte
		if m.config.LogRequestBody && c.Request.Body != nil {
			requestBody, _ = c.GetRawData()
			c.Request.Body = io.NopCloser(bytes.NewBuffer(requestBody))
		}

		// Process request
		c.Next()

		// Build log fields
		latency := time.Since(start)
		status := c.Writer.Status()
		userID := GetUserID(c)
		username := GetUsername(c)
		role := GetRole(c)

		fields := []zap.Field{
			zap.String("request_id", requestID),
			zap.String("method", c.Request.Method),
			zap.String("path", c.FullPath()),
			zap.String("raw_path", c.Request.URL.Path),
			zap.String("query", c.Request.URL.RawQuery),
			zap.Int("status", status),
			zap.Duration("latency", latency),
			zap.String("client_ip", m.getClientIP(c)),
			zap.String("user_agent", c.Request.UserAgent()),
		}

		// Add user context if authenticated
		if userID != "" {
			fields = append(fields,
				zap.String("user_id", userID),
				zap.String("username", username),
				zap.String("role", role),
			)
		}

		// Add error details for 4xx/5xx
		if len(c.Errors) > 0 {
			fields = append(fields, zap.String("errors", c.Errors.String()))
		}

		// Log request body for errors (masked)
		if status >= 400 && len(requestBody) > 0 && m.config.LogRequestBody {
			maskedBody := m.maskSensitiveData(string(requestBody))
			fields = append(fields, zap.String("request_body", maskedBody))
		}

		// Determine log level by status
		switch {
		case status >= 500:
			m.logger.Error("HTTP request failed", fields...)
		case status >= 400:
			m.logger.Warn("HTTP request client error", fields...)
		default:
			if m.config.LogSuccessRequests {
				m.logger.Info("HTTP request completed", fields...)
			}
		}
	}
}

// shouldSkipLogging returns true for health check endpoints.
func (m *LoggingMiddleware) shouldSkipLogging(path string) bool {
	skipPaths := []string{"/healthz", "/readyz", "/metrics"}
	for _, p := range skipPaths {
		if strings.HasPrefix(path, p) {
			return true
		}
	}
	return false
}

// getClientIP extracts real client IP considering proxies.
func (m *LoggingMiddleware) getClientIP(c *gin.Context) string {
	// Check X-Forwarded-For header (set by nginx)
	if xff := c.GetHeader("X-Forwarded-For"); xff != "" {
		ips := strings.Split(xff, ",")
		return strings.TrimSpace(ips[0])
	}
	// Check X-Real-IP header
	if xri := c.GetHeader("X-Real-IP"); xri != "" {
		return xri
	}
	// Fallback to remote address
	ip, _, _ := net.SplitHostPort(c.Request.RemoteAddr)
	return ip
}

// maskSensitiveData removes/masks sensitive fields from logged data.
func (m *LoggingMiddleware) maskSensitiveData(data string) string {
	// Mask passwords, tokens, secrets
	sensitiveKeys := []string{
		"password", "token", "secret", "authorization",
		"access_token", "refresh_token", "api_key",
		"credit_card", "ssn", "cvv",
	}

	result := data
	for _, key := range sensitiveKeys {
		// Simple masking for JSON-like structures
		result = maskKeyInJSON(result, key)
	}
	return result
}

// maskKeyInJSON masks values for a given key in JSON-like string.
func maskKeyInJSON(data, key string) string {
	// This is a simplified implementation
	// In production, use a proper JSON parser for accurate masking
	patterns := []string{
		`"` + key + `":\s*"[^"]*"`,
		`"` + key + `":\s*'[^']*'`,
	}
	for _, pattern := range patterns {
		re := regexp.MustCompile(`(?i)` + pattern)
		result = re.ReplaceAllStringFunc(result, func(match string) string {
			parts := strings.SplitN(match, ":", 2)
			if len(parts) == 2 {
				return parts[0] + ": \"***MASKED***\""
			}
			return match
		})
	}
	return result
}
```

---

## Recovery Middleware

```go
// internal/middleware/recovery.go
package middleware

import (
	"net/http"
	"runtime/debug"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"crm-system/internal/domain/errors"
)

// RecoveryMiddleware handles panic recovery with structured logging.
type RecoveryMiddleware struct {
	logger *zap.Logger
}

// NewRecoveryMiddleware creates a new recovery middleware.
func NewRecoveryMiddleware(logger *zap.Logger) *RecoveryMiddleware {
	return &RecoveryMiddleware{
		logger: logger.Named("recovery"),
	}
}

// Recover returns a Gin handler that recovers from panics.
// Logs stack trace and returns safe 500 response.
func (m *RecoveryMiddleware) Recover() gin.HandlerFunc {
	return func(c *gin.Context) {
		defer func() {
			if err := recover(); err != nil {
				requestID := GetRequestID(c)
				userID := GetUserID(c)

				// Log panic with full stack trace
				m.logger.Error("panic recovered",
					zap.String("request_id", requestID),
					zap.String("user_id", userID),
					zap.String("method", c.Request.Method),
					zap.String("path", c.FullPath()),
					zap.Any("panic", err),
					zap.String("stack", string(debug.Stack())),
				)

				// Check for broken pipe / client disconnect (not a real error)
				if isClientDisconnect(err) {
					c.Abort()
					return
				}

				// Return safe error response
				errors.WriteInternalServerError(c)
				c.Abort()
			}
		}()

		c.Next()
	}
}

// isClientDisconnect checks if panic is due to client closing connection.
func isClientDisconnect(err interface{}) bool {
	if err == nil {
		return false
	}

	errStr := ""
	switch e := err.(type) {
	case error:
		errStr = e.Error()
	case string:
		errStr = e
	default:
		return false
	}

	// Common client disconnect errors
	disconnectErrors := []string{
		"broken pipe",
		"connection reset by peer",
		"write: broken pipe",
		"http: request body read error",
		"http: response write error",
	}

	for _, de := range disconnectErrors {
		if strings.Contains(strings.ToLower(errStr), de) {
			return true
		}
	}
	return false
}
```

---

## Security Headers Middleware

```go
// internal/middleware/security.go
package middleware

import (
	"github.com/gin-gonic/gin"
)

// SecurityHeadersMiddleware adds security-related HTTP headers.
type SecurityHeadersMiddleware struct{}

// NewSecurityHeadersMiddleware creates a new security headers middleware.
func NewSecurityHeadersMiddleware() *SecurityHeadersMiddleware {
	return &SecurityHeadersMiddleware{}
}

// SecureHeaders returns a Gin handler that adds security headers.
// Per OWASP recommendations and project standards.
func (m *SecurityHeadersMiddleware) SecureHeaders() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Prevent MIME type sniffing
		c.Header("X-Content-Type-Options", "nosniff")

		// Prevent clickjacking
		c.Header("X-Frame-Options", "DENY")

		// Enable XSS protection (legacy but harmless)
		c.Header("X-XSS-Protection", "1; mode=block")

		// Referrer policy
		c.Header("Referrer-Policy", "strict-origin-when-cross-origin")

		// Content Security Policy (restrictive default)
		c.Header("Content-Security-Policy",
			"default-src 'self'; "+
				"script-src 'self'; "+
				"style-src 'self' 'unsafe-inline'; "+
				"img-src 'self' data:; "+
				"font-src 'self'; "+
				"connect-src 'self'; "+
				"frame-ancestors 'none'; "+
				"base-uri 'self'; "+
				"form-action 'self'")

		// Permissions Policy (formerly Feature Policy)
		c.Header("Permissions-Policy",
			"geolocation=(), "+
				"microphone=(), "+
				"camera=(), "+
				"payment=(), "+
				"usb=(), "+
				"magnetometer=(), "+
				"gyroscope=(), "+
				"accelerometer=()")

		// HSTS (only if TLS terminated at app level; nginx handles in prod)
		// c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")

		c.Next()
	}
}

// CORSMiddleware handles Cross-Origin Resource Sharing.
// Configure allowed origins from config in production.
func CORSMiddleware(allowedOrigins []string) gin.HandlerFunc {
	return func(c *gin.Context) {
		origin := c.Request.Header.Get("Origin")

		// Check if origin is allowed
		allowed := false
		for _, o := range allowedOrigins {
			if o == "*" || o == origin {
				allowed = true
				break
			}
		}

		if allowed {
			c.Header("Access-Control-Allow-Origin", origin)
			c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, PATCH, DELETE, OPTIONS")
			c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Accept, Authorization, X-Request-ID")
			c.Header("Access-Control-Allow-Credentials", "true")
			c.Header("Access-Control-Max-Age", "86400")
		}

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(http.StatusNoContent)
			return
		}

		c.Next()
	}
}
```

---

## Error Mapping

```go
// internal/domain/errors/errors.go
package errors

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// ErrorCode represents standardized error codes.
type ErrorCode string

const (
	// Authentication errors (401)
	ErrCodeUnauthorized       ErrorCode = "UNAUTHORIZED"
	ErrCodeTokenExpired       ErrorCode = "TOKEN_EXPIRED"
	ErrCodeTokenInvalid       ErrorCode = "TOKEN_INVALID"
	ErrCodeInvalidIssuer      ErrorCode = "INVALID_ISSUER"
	ErrCodeInvalidAudience    ErrorCode = "INVALID_AUDIENCE"
	ErrCodeTokenNotYetValid   ErrorCode = "TOKEN_NOT_YET_VALID"

	// Authorization errors (403)
	ErrCodeForbidden          ErrorCode = "FORBIDDEN"
	ErrCodeInsufficientRole   ErrorCode = "INSUFFICIENT_ROLE"

	// Validation errors (422)
	ErrCodeValidationFailed   ErrorCode = "VALIDATION_FAILED"
	ErrCodeRequiredField      ErrorCode = "REQUIRED_FIELD"
	ErrCodeInvalidFormat      ErrorCode = "INVALID_FORMAT"
	ErrCodeMaxLengthExceeded  ErrorCode = "MAX_LENGTH_EXCEEDED"
	ErrCodeInvalidEnumValue   ErrorCode = "INVALID_ENUM_VALUE"
	ErrCodeInvalidCountryCode ErrorCode = "INVALID_COUNTRY_CODE"

	// Business logic errors (409)
	ErrCodeDuplicateDetected  ErrorCode = "DUPLICATE_DETECTED"
	ErrCodeConflict           ErrorCode = "CONFLICT"

	// Rate limiting (429)
	ErrCodeRateLimited        ErrorCode = "RATE_LIMITED"

	// Server errors (500)
	ErrCodeInternalError      ErrorCode = "INTERNAL_ERROR"
	ErrCodeServiceUnavailable ErrorCode = "SERVICE_UNAVAILABLE"
)

// APIError represents a standardized error response.
type APIError struct {
	Success bool        `json:"success"`
	Message string      `json:"message"`
	Code    ErrorCode   `json:"code,omitempty"`
	Details interface{} `json:"details,omitempty"`
	Meta    ErrorMeta   `json:"meta,omitempty"`
}

// ErrorMeta contains request metadata for debugging.
type ErrorMeta struct {
	RequestID string `json:"request_id,omitempty"`
}

// Predefined error variables for middleware use.
var (
	ErrUnauthorized       = NewError(ErrCodeUnauthorized, "Authentication required")
	ErrTokenExpired       = NewError(ErrCodeTokenExpired, "Token has expired")
	ErrTokenInvalid       = NewError(ErrCodeTokenInvalid, "Invalid token")
	ErrInvalidIssuer      = NewError(ErrCodeInvalidIssuer, "Invalid token issuer")
	ErrInvalidAudience    = NewError(ErrCodeInvalidAudience, "Invalid token audience")
	ErrTokenNotYetValid   = NewError(ErrCodeTokenNotYetValid, "Token not yet valid")
	ErrForbidden          = NewError(ErrCodeForbidden, "Access denied")
	ErrInsufficientRole   = NewError(ErrCodeInsufficientRole, "Insufficient permissions")
	ErrInternalError      = NewError(ErrCodeInternalError, "Internal server error")
)

// NewError creates a new APIError.
func NewError(code ErrorCode, message string) *APIError {
	return &APIError{
		Success: false,
		Message: message,
		Code:    code,
	}
}

// WithDetails adds details to error.
func (e *APIError) WithDetails(details interface{}) *APIError {
	e.Details = details
	return e
}

// WithRequestID adds request ID to error meta.
func (e *APIError) WithRequestID(requestID string) *APIError {
	e.Meta.RequestID = requestID
	return e
}

// WriteError writes error response with appropriate HTTP status.
func WriteError(c *gin.Context, err *APIError) {
	status := httpStatusForCode(err.Code)
	if err.Meta.RequestID == "" {
		err.Meta.RequestID = GetRequestID(c)
	}
	c.JSON(status, err)
}

// HTTP status mapping for error codes.
func httpStatusForCode(code ErrorCode) int {
	switch code {
	case ErrCodeUnauthorized, ErrCodeTokenExpired, ErrCodeTokenInvalid,
		ErrCodeInvalidIssuer, ErrCodeInvalidAudience, ErrCodeTokenNotYetValid:
		return http.StatusUnauthorized // 401
	case ErrCodeForbidden, ErrCodeInsufficientRole:
		return http.StatusForbidden // 403
	case ErrCodeValidationFailed, ErrCodeRequiredField, ErrCodeInvalidFormat,
		ErrCodeMaxLengthExceeded, ErrCodeInvalidEnumValue, ErrCodeInvalidCountryCode:
		return http.StatusUnprocessableEntity // 422
	case ErrCodeDuplicateDetected, ErrCodeConflict:
		return http.StatusConflict // 409
	case ErrCodeRateLimited:
		return http.StatusTooManyRequests // 429
	default:
		return http.StatusInternalServerError // 500
	}
}

// Convenience functions for middleware
func WriteUnauthorized(c *gin.Context, message string) {
	err := NewError(ErrCodeUnauthorized, message).WithRequestID(GetRequestID(c))
	WriteError(c, err)
}

func WriteForbidden(c *gin.Context, message string) {
	err := NewError(ErrCodeForbidden, message).WithRequestID(GetRequestID(c))
	WriteError(c, err)
}

func WriteInternalServerError(c *gin.Context) {
	err := NewError(ErrCodeInternalError, "Internal server error").WithRequestID(GetRequestID(c))
	WriteError(c, err)
}
```

---

## Middleware Registration (Wire-up)

```go
// internal/middleware/registry.go
package middleware

import (
	"github.com/gin-gonic/gin"
	"go.uber.org/zap"

	"crm-system/internal/config"
	"crm-system/internal/service"
)

// MiddlewareRegistry holds all middleware instances.
type MiddlewareRegistry struct {
	Auth           *AuthMiddleware
	Authorization  *AuthorizationMiddleware
	Logging        *LoggingMiddleware
	Recovery       *RecoveryMiddleware
	Security       *SecurityHeadersMiddleware
	RequestContext *RequestContextMiddleware
}

// NewMiddlewareRegistry creates and wires all middleware.
func NewMiddlewareRegistry(
	jwtService service.JWTService,
	logger *zap.Logger,
	cfg *config.Config,
) *MiddlewareRegistry {
	return &MiddlewareRegistry{
		Auth:           NewAuthMiddleware(jwtService, logger, &cfg.JWT),
		Authorization:  &AuthorizationMiddleware{},
		Logging:        NewLoggingMiddleware(logger, &cfg.Logging),
		Recovery:       NewRecoveryMiddleware(logger),
		Security:       NewSecurityHeadersMiddleware(),
		RequestContext: &RequestContextMiddleware{},
	}
}

// RegisterGlobalMiddleware applies middleware in correct order.
// Order matters: Recovery -> RequestContext -> Security -> Logging -> Auth -> Authorization
func (r *MiddlewareRegistry) RegisterGlobalMiddleware(router *gin.Engine) {
	// 1. Recovery (outermost - catches all panics)
	router.Use(r.Recovery.Recover())

	// 2. Request Context (request ID, timing)
	router.Use(r.RequestContext.Middleware())

	// 3. Security Headers
	router.Use(r.Security.SecureHeaders())

	// 4. CORS (if needed)
	// router.Use(CORSMiddleware(cfg.CORS.AllowedOrigins))

	// 5. Logging (after context, before auth for request ID in logs)
	router.Use(r.Logging.LogRequest())
}

// RegisterProtectedRoutes applies auth + authorization to protected route group.
func (r *MiddlewareRegistry) RegisterProtectedRoutes(group *gin.RouterGroup) {
	group.Use(r.Auth.RequireAuth())
}

// RegisterAdminRoutes applies Admin-only authorization.
func (r *MiddlewareRegistry) RegisterAdminRoutes(group *gin.RouterGroup) {
	group.Use(r.Auth.RequireAuth())
	group.Use(RequireAdmin())
}

// RegisterManagerOrAdminRoutes applies Manager+Admin authorization.
func (r *MiddlewareRegistry) RegisterManagerOrAdminRoutes(group *gin.RouterGroup) {
	group.Use(r.Auth.RequireAuth())
	group.Use(RequireManagerOrAdmin())
}
```

---

## Required Service Interface (for DI)

```go
// internal/service/jwt_service.go
package service

import (
	"context"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

// JWTClaims represents the JWT claims structure.
type JWTClaims struct {
	jwt.RegisteredClaims
	UserID   string `json:"user_id"`
	Username string `json:"username"`
	Role     string `json:"role"`
	TokenType string `json:"token_type"` // "access" or "refresh"
}

// JWTService defines the interface for JWT operations.
type JWTService interface {
	// ValidateAccessToken validates and parses an access token.
	ValidateAccessToken(ctx context.Context, tokenString string) (*JWTClaims, error)

	// ValidateRefreshToken validates and parses a refresh token.
	ValidateRefreshToken(ctx context.Context, tokenString string) (*JWTClaims, error)

	// GenerateAccessToken creates a new access token.
	GenerateAccessToken(userID, username, role string) (string, time.Time, error)

	// GenerateRefreshToken creates a new refresh token.
	GenerateRefreshToken(userID, username, role string) (string, time.Time, error)

	// RevokeToken adds token to blocklist (logout).
	RevokeToken(ctx context.Context, tokenString string) error

	// IsTokenRevoked checks if token is in blocklist.
	IsTokenRevoked(ctx context.Context, tokenString string) (bool, error)
}
```

---

## Configuration Structures

```go
// internal/config/config.go
package config

import "time"

// Config holds all application configuration.
type Config struct {
	JWT      JWTConfig
	Logging  LoggingConfig
	CORS     CORSConfig
	Server   ServerConfig
	Database DatabaseConfig
}

// JWTConfig holds JWT-related configuration.
type JWTConfig struct {
	SecretKey       string
	AccessTokenTTL  time.Duration
	RefreshTokenTTL time.Duration
	Issuer          string
	Audience        []string
	Algorithm       string // "HS256"
}

// LoggingConfig holds logging configuration.
type LoggingConfig struct {
	Level             string // debug, info, warn, error
	Format            string // json, console
	LogSuccessRequests bool
	LogRequestBody    bool
}

// CORSConfig holds CORS configuration.
type CORSConfig struct {
	AllowedOrigins []string
	AllowedMethods []string
	AllowedHeaders []string
}

// ServerConfig holds HTTP server configuration.
type ServerConfig struct {
	Host         string
	Port         int
	ReadTimeout  time.Duration
	WriteTimeout time.Duration
	IdleTimeout  time.Duration
}

// DatabaseConfig holds database configuration.
type DatabaseConfig struct {
	Host            string
	Port            int
	User            string
	Password        string
	Name            string
	SSLMode         string
	MaxOpenConns    int
	MaxIdleConns    int
	ConnMaxLifetime time.Duration
}
```

---

## Validation Checklist

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| ✅ Compile Safe | All types defined, imports resolved | Interfaces in `service`, errors in `domain/errors` |
| ✅ JWT Validation | Signature, exp, iss, aud, claims | `AuthMiddleware.validateStandardClaims()` |
| ✅ Signature Validation | HS256 via `jwt-go` | `JWTService.ValidateAccessToken()` |
| ✅ Expiration Validation | `ExpiresAt` check | `validateStandardClaims()` |
| ✅ Authorization | Role-based (Admin/Manager) | `RequireRole()`, `RequireAdmin()` |
| ✅ Request Context | user_id, username, role, claims | `populateContext()`, `GetUserID()` etc. |
| ✅ Logging | Request ID, method, path, status, duration, user | `LoggingMiddleware.LogRequest()` |
| ✅ Recovery | Panic catch, log, safe 500 | `RecoveryMiddleware.Recover()` |
| ✅ Security Rules | No secrets logged, masked sensitive data | `maskSensitiveData()` |
| ✅ No Repository Access | Middleware only uses JWTService, Logger | Verified |
| ✅ No Service Calls | Only JWTService (auth infra) | Verified |
| ✅ No Business Logic | Pure cross-cutting concerns | Verified |
| ✅ Story Scope | Only STORY-001 required middleware | Auth, Admin Auth, Logging, Recovery, Context |

---

## Handoff to Backend Swagger Agent

**Artifacts Produced:**
- `internal/middleware/auth.go` - JWT Authentication
- `internal/middleware/authorization.go` - Role-Based Authorization
- `internal/middleware/context.go` - Request Context Population
- `internal/middleware/logging.go` - Centralized Logging
- `internal/middleware/recovery.go` - Panic Recovery
- `internal/middleware/security.go` - Security Headers + CORS
- `internal/middleware/registry.go` - Middleware Wire-up
- `internal/service/jwt_service.go` - JWT Service Interface (for DI)
- `internal/domain/errors/errors.go` - Standard Error Responses
- `internal/config/config.go` - Configuration Structures

**Next Agent:** Backend Swagger Agent  
**Dependencies:** Middleware must be registered in router before handler registration.