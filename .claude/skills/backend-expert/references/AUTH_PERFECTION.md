# ULTIMATE AUTHENTICATION & AUTHORIZATION REFERENCE

## 1. JWT IMPLEMENTATION (PERFECTION)

### 1.1 JWT Generation with All Security Features

```typescript
// src/utils/jwt.ts
import jwt from 'jsonwebtoken';
import { randomBytes } from 'crypto';

interface JWTPayload {
    sub: string; // Subject (user ID)
    email: string;
    role: string;
    permissions: string[];
    aud: string; // Audience
    iss: string; // Issuer
    jti: string; // JWT ID (for blacklisting)
    iat: number; // Issued at
    exp: number; // Expiration
    nbf: number; // Not before
}

/**
 * Generate JWT with maximum security
 * PERFECTION: All security considerations
 */
export function generateJWT(
    userId: string,
    email: string,
    role: string,
    permissions: string[],
    expiresIn: string = '15m'
): { token: string; expiresAt: number } {
    const now = Math.floor(Date.now() / 1000);
    const jti = randomBytes(16).toString('hex'); // Unique token ID

    const payload: JWTPayload = {
        sub: userId,
        email,
        role,
        permissions,
        aud: process.env.JWT_AUDIENCE || 'app',
        iss: process.env.JWT_ISSUER || 'auth-service',
        jti, // For revocation
        iat: now,
        nbf: now, // Valid immediately
        exp: now + getExpirationSeconds(expiresIn),
    };

    const token = jwt.sign(payload, process.env.JWT_SECRET!, {
        algorithm: 'HS256',
        encoding: 'utf8',
        noTimestamp: false, // Include iat claim
    });

    return {
        token,
        expiresAt: payload.exp * 1000,
    };
}

/**
 * Verify JWT with all checks
 */
export function verifyJWT(token: string): JWTPayload | null {
    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET!, {
            algorithms: ['HS256'],
            audience: process.env.JWT_AUDIENCE,
            issuer: process.env.JWT_ISSUER,
            clockTimestamp: Math.floor(Date.now() / 1000),
            clockTolerance: 0, // No clock skew tolerance
        }) as JWTPayload;

        // Additional checks
        if (!decoded.sub || !decoded.email) {
            return null;
        }

        // Check if blacklisted
        if (isTokenBlacklisted(decoded.jti)) {
            return null;
        }

        return decoded;
    } catch (error) {
        if (error instanceof jwt.TokenExpiredError) {
            console.error('Token expired at', error.expiredAt);
        } else if (error instanceof jwt.JsonWebTokenError) {
            console.error('Token verification failed:', error.message);
        }
        return null;
    }
}

/**
 * Refresh token pair (access + refresh)
 * PERFECTION: Token rotation
 */
export function refreshTokenPair(
    userId: string,
    email: string,
    role: string,
    permissions: string[]
): { accessToken: string; refreshToken: string; expiresAt: number } {
    // New access token (short-lived)
    const { token: accessToken, expiresAt } = generateJWT(
        userId,
        email,
        role,
        permissions,
        '15m'
    );

    // New refresh token (long-lived)
    const { token: refreshToken } = generateJWT(
        userId,
        email,
        role,
        permissions,
        '7d'
    );

    return { accessToken, refreshToken, expiresAt };
}

/**
 * Revoke token (add to blacklist)
 */
export async function revokeToken(jti: string, expiresAt: number): Promise<void> {
    // Calculate TTL (Time To Live)
    const ttl = Math.ceil((expiresAt - Date.now()) / 1000);

    // Store in Redis with TTL
    if (ttl > 0) {
        await cache.setex(`blacklist:${jti}`, ttl, '1');
    }
}

/**
 * Check if token is blacklisted
 */
function isTokenBlacklisted(jti: string): boolean {
    return cache.exists(`blacklist:${jti}`);
}

function getExpirationSeconds(expiresIn: string): number {
    const units: Record<string, number> = {
        s: 1,
        m: 60,
        h: 3600,
        d: 86400,
    };

    const match = expiresIn.match(/^(\d+)([smhd])$/);
    if (!match) return 900; // Default 15 minutes

    return parseInt(match[1]) * units[match[2]];
}
```

### 1.2 JWT-based Login Flow (Complete)

```typescript
// src/services/auth.service.ts
import bcrypt from 'bcryptjs';
import { generateJWT, refreshTokenPair, revokeToken } from '@/utils/jwt';

/**
 * Login with email and password
 * PERFECTION: Security hardened
 */
export async function login(
    email: string,
    password: string,
    ipAddress: string
): Promise<{
    accessToken: string;
    refreshToken: string;
    user: UserDTO;
}> {
    // 1. Find user by email
    const user = await db.user.findUnique({ where: { email } });

    if (!user) {
        // Log attempt
        await logLoginAttempt(email, ipAddress, false);

        // Return generic error (don't reveal if email exists)
        throw new UnauthorizedError('Invalid credentials');
    }

    // 2. Check if account is locked
    if (user.isLocked) {
        throw new UnauthorizedError('Account is locked');
    }

    // 3. Check if email is verified
    if (!user.emailVerified) {
        throw new UnauthorizedError('Please verify your email first');
    }

    // 4. Verify password
    const isPasswordValid = await bcrypt.compare(password, user.hashedPassword);

    if (!isPasswordValid) {
        // Increment failed login attempts
        await incrementFailedLoginAttempts(user.id);

        // Lock account if too many attempts
        if (user.failedLoginAttempts >= 5) {
            await db.user.update({
                where: { id: user.id },
                data: { isLocked: true },
            });

            await sendAccountLockedEmail(user.email);
            throw new UnauthorizedError('Too many failed attempts. Account locked.');
        }

        // Log failed attempt
        await logLoginAttempt(email, ipAddress, false);

        throw new UnauthorizedError('Invalid credentials');
    }

    // 5. Check if MFA is enabled
    if (user.mfaEnabled) {
        // Create temporary token for MFA verification
        const mfaToken = generateMFAToken(user.id);
        return {
            mfaToken,
            user: mapUserToDTO(user),
        } as any;
    }

    // 6. Reset failed login attempts
    await db.user.update({
        where: { id: user.id },
        data: { failedLoginAttempts: 0 },
    });

    // 7. Generate tokens
    const { accessToken, refreshToken } = refreshTokenPair(
        user.id,
        user.email,
        user.role,
        user.permissions
    );

    // 8. Store refresh token
    await storeRefreshToken(
        user.id,
        refreshToken,
        ipAddress
    );

    // 9. Log successful login
    await logLoginAttempt(email, ipAddress, true);

    return {
        accessToken,
        refreshToken,
        user: mapUserToDTO(user),
    };
}

/**
 * Logout and revoke tokens
 */
export async function logout(
    userId: string,
    jti: string,
    expiresAt: number
): Promise<void> {
    // Revoke access token
    await revokeToken(jti, expiresAt);

    // Revoke all refresh tokens
    await db.refreshToken.deleteMany({
        where: { userId },
    });

    // Log logout
    await logSecurityEvent({
        type: 'logout',
        userId,
        timestamp: new Date(),
    });
}

/**
 * Refresh token endpoint
 */
export async function refreshTokens(
    refreshToken: string,
    ipAddress: string
): Promise<{ accessToken: string; refreshToken: string }> {
    // Verify refresh token
    const payload = verifyJWT(refreshToken);

    if (!payload) {
        throw new UnauthorizedError('Invalid refresh token');
    }

    // Check if refresh token exists in database
    const storedToken = await db.refreshToken.findUnique({
        where: {
            token: refreshToken,
        },
    });

    if (!storedToken || storedToken.revokedAt) {
        throw new UnauthorizedError('Refresh token has been revoked');
    }

    // Fetch user
    const user = await db.user.findUnique({
        where: { id: payload.sub },
    });

    if (!user) {
        throw new UnauthorizedError('User not found');
    }

    // Revoke old refresh token
    await db.refreshToken.update({
        where: { id: storedToken.id },
        data: { revokedAt: new Date() },
    });

    // Generate new token pair
    const { accessToken: newAccessToken, refreshToken: newRefreshToken } =
        refreshTokenPair(
            user.id,
            user.email,
            user.role,
            user.permissions
        );

    // Store new refresh token
    await storeRefreshToken(user.id, newRefreshToken, ipAddress);

    return {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
    };
}
```

## 2. SESSION-BASED AUTHENTICATION

### 2.1 Session Management (Express)

```typescript
// src/config/session.ts
import session from 'express-session';
import RedisStore from 'connect-redis';
import { redis } from '@/core/cache';

/**
 * Configure session middleware
 * PERFECTION: Secure session handling
 */
export const sessionMiddleware = session({
    store: new RedisStore({ client: redis }),
    secret: process.env.SESSION_SECRET!,
    resave: false,
    saveUninitialized: false,
    proxy: true, // Trust proxy (for HTTPS)
    cookie: {
        secure: process.env.NODE_ENV === 'production', // HTTPS only
        httpOnly: true, // Prevent JavaScript access (XSS protection)
        sameSite: 'strict', // CSRF protection
        maxAge: 24 * 60 * 60 * 1000, // 24 hours
        domain: process.env.COOKIE_DOMAIN,
        path: '/',
    },
    name: 'sessionId', // Don't use default 'connect.sid'
});

// src/routes/auth.routes.ts
router.post('/login', async (req: Request, res: Response) => {
    const { email, password } = req.body;

    // Authenticate user
    const user = await authenticateUser(email, password);

    // Create session
    (req.session as any).userId = user.id;
    (req.session as any).user = {
        id: user.id,
        email: user.email,
        role: user.role,
    };

    // Session is automatically sent as Set-Cookie header
    res.json({ message: 'Logged in' });
});

router.post('/logout', (req: Request, res: Response) => {
    req.session.destroy((err) => {
        if (err) {
            res.status(500).json({ error: 'Logout failed' });
            return;
        }
        res.clearCookie('sessionId');
        res.json({ message: 'Logged out' });
    });
});
```

## 3. OAUTH2 IMPLEMENTATION

### 3.1 Google OAuth2 (Complete)

```typescript
// src/services/oauth.service.ts
import { google } from 'googleapis';

const oauth2Client = new google.auth.OAuth2(
    process.env.GOOGLE_CLIENT_ID,
    process.env.GOOGLE_CLIENT_SECRET,
    process.env.GOOGLE_REDIRECT_URI
);

/**
 * Generate OAuth2 authorization URL
 */
export function getGoogleAuthURL(): string {
    return oauth2Client.generateAuthUrl({
        access_type: 'offline',
        scope: [
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ],
        // State for CSRF protection
        state: generateRandomState(),
    });
}

/**
 * Exchange authorization code for tokens
 */
export async function exchangeCodeForTokens(code: string) {
    try {
        const { tokens } = await oauth2Client.getToken(code);

        // Verify the token was issued to our app
        const ticket = await oauth2Client.verifyIdToken({
            idToken: tokens.id_token,
            audience: process.env.GOOGLE_CLIENT_ID,
        });

        const payload = ticket.getPayload();

        return {
            email: payload.email,
            name: payload.name,
            picture: payload.picture,
            googleId: payload.sub,
            accessToken: tokens.access_token,
        };
    } catch (error) {
        throw new UnauthorizedError('Failed to authenticate with Google');
    }
}

/**
 * Handle OAuth callback
 */
export async function handleOAuthCallback(
    code: string,
    state: string
): Promise<{ accessToken: string; user: UserDTO }> {
    // Verify state (CSRF protection)
    if (!verifyState(state)) {
        throw new UnauthorizedError('Invalid state parameter');
    }

    // Exchange code for Google tokens
    const googleUser = await exchangeCodeForTokens(code);

    // Find or create user
    let user = await db.user.findUnique({
        where: { email: googleUser.email },
    });

    if (!user) {
        user = await db.user.create({
            data: {
                email: googleUser.email,
                name: googleUser.name,
                googleId: googleUser.googleId,
                emailVerified: true, // Google verified the email
                profile: {
                    picture: googleUser.picture,
                },
            },
        });
    }

    // Generate our JWT
    const { accessToken } = generateJWT(
        user.id,
        user.email,
        user.role,
        user.permissions
    );

    return {
        accessToken,
        user: mapUserToDTO(user),
    };
}
```

## 4. MULTI-FACTOR AUTHENTICATION (MFA)

### 4.1 TOTP Implementation

```typescript
// src/services/mfa.service.ts
import speakeasy from 'speakeasy';
import QRCode from 'qrcode';

/**
 * Generate TOTP secret and QR code
 */
export async function generateMFASecret(
    email: string
): Promise<{ secret: string; qrCode: string }> {
    const secret = speakeasy.generateSecret({
        name: `MyApp (${email})`,
        issuer: 'MyApp',
        length: 32,
    });

    const qrCode = await QRCode.toDataURL(secret.otpauth_url);

    return {
        secret: secret.base32,
        qrCode,
    };
}

/**
 * Verify TOTP token
 */
export function verifyMFAToken(secret: string, token: string): boolean {
    return speakeasy.totp.verify({
        secret,
        encoding: 'base32',
        token,
        window: 2, // Allow 2 time windows (±30 seconds)
    });
}

/**
 * Enable MFA for user
 */
export async function enableMFA(
    userId: string,
    secret: string,
    mfaToken: string
): Promise<void> {
    // Verify token first
    if (!verifyMFAToken(secret, mfaToken)) {
        throw new BadRequestError('Invalid MFA token');
    }

    // Store secret
    await db.user.update({
        where: { id: userId },
        data: {
            mfaEnabled: true,
            mfaSecret: secret,
        },
    });

    // Generate backup codes
    const backupCodes = generateBackupCodes(10);
    await saveBackupCodes(userId, backupCodes);
}

/**
 * Verify MFA during login
 */
export async function verifyMFALogin(
    userId: string,
    mfaToken: string
): Promise<boolean> {
    const user = await db.user.findUnique({
        where: { id: userId },
    });

    if (!user?.mfaSecret) {
        return false;
    }

    // Try regular TOTP
    if (verifyMFAToken(user.mfaSecret, mfaToken)) {
        return true;
    }

    // Try backup code
    const backupCode = await db.backupCode.findFirst({
        where: {
            userId,
            code: mfaToken,
            usedAt: null,
        },
    });

    if (backupCode) {
        // Mark as used
        await db.backupCode.update({
            where: { id: backupCode.id },
            data: { usedAt: new Date() },
        });
        return true;
    }

    return false;
}
```

## 5. PERMISSION & ROLE MANAGEMENT (PERFECTION)

### 5.1 Database Schema

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    hashedPassword VARCHAR,
    role_id UUID REFERENCES roles(id),
    mfaEnabled BOOLEAN DEFAULT false,
    mfaSecret VARCHAR,
    emailVerified BOOLEAN DEFAULT false,
    isLocked BOOLEAN DEFAULT false,
    failedLoginAttempts INT DEFAULT 0,
    lastLoginAt TIMESTAMP,
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW()
);

-- Roles table
CREATE TABLE roles (
    id UUID PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    createdAt TIMESTAMP DEFAULT NOW()
);

-- Permissions table
CREATE TABLE permissions (
    id UUID PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    description TEXT,
    resource VARCHAR NOT NULL, -- 'users', 'products', 'orders'
    action VARCHAR NOT NULL, -- 'create', 'read', 'update', 'delete'
    createdAt TIMESTAMP DEFAULT NOW()
);

-- Role-Permission junction
CREATE TABLE role_permissions (
    role_id UUID REFERENCES roles(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    PRIMARY KEY (role_id, permission_id)
);

-- User-specific permissions (override)
CREATE TABLE user_permissions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    permission_id UUID REFERENCES permissions(id) ON DELETE CASCADE,
    grantedAt TIMESTAMP DEFAULT NOW(),
    expiresAt TIMESTAMP, -- Temporary permission
    UNIQUE(user_id, permission_id)
);

-- Audit log
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR NOT NULL,
    resource VARCHAR NOT NULL,
    resourceId VARCHAR,
    changes JSONB,
    ipAddress VARCHAR,
    userAgent TEXT,
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX (user_id, timestamp)
);
```

### 5.2 Permission Service

```typescript
// src/services/permission.service.ts

/**
 * Check if user has permission
 */
export async function userHasPermission(
    userId: string,
    requiredPermission: string
): Promise<boolean> {
    // Admin bypass
    const user = await db.user.findUnique({
        where: { id: userId },
        include: { role: { include: { permissions: true } } },
    });

    if (user?.role?.name === 'admin') {
        return true;
    }

    // Check role permissions
    const hasRolePermission = user?.role?.permissions.some(
        (p) => p.name === requiredPermission
    );

    if (hasRolePermission) {
        return true;
    }

    // Check user-specific permissions
    const hasUserPermission = await db.userPermission.findFirst({
        where: {
            userId,
            permission: { name: requiredPermission },
            OR: [
                { expiresAt: null }, // Permanent
                { expiresAt: { gt: new Date() } }, // Not expired
            ],
        },
    });

    return !!hasUserPermission;
}

/**
 * Grant temporary permission
 */
export async function grantTemporaryPermission(
    userId: string,
    permissionName: string,
    expiresIn: number // milliseconds
): Promise<void> {
    const permission = await db.permission.findUnique({
        where: { name: permissionName },
    });

    if (!permission) {
        throw new NotFoundError('Permission not found');
    }

    await db.userPermission.create({
        data: {
            userId,
            permissionId: permission.id,
            expiresAt: new Date(Date.now() + expiresIn),
        },
    });
}

/**
 * Revoke permission
 */
export async function revokePermission(
    userId: string,
    permissionName: string
): Promise<void> {
    await db.userPermission.deleteMany({
        where: {
            userId,
            permission: { name: permissionName },
        },
    });
}

/**
 * Audit log an action
 */
export async function auditLog(
    userId: string,
    action: string,
    resource: string,
    resourceId: string,
    changes?: Record<string, any>,
    ipAddress?: string,
    userAgent?: string
): Promise<void> {
    await db.auditLog.create({
        data: {
            userId,
            action,
            resource,
            resourceId,
            changes,
            ipAddress,
            userAgent,
            timestamp: new Date(),
        },
    });
}
```

This covers COMPLETE authentication and authorization in PERFECTION!