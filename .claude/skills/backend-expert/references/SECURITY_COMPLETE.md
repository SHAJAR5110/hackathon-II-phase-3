# ULTIMATE BACKEND SECURITY HARDENING

## 1. SQL INJECTION PREVENTION

### 1.1 Using ORMs (SAFE)

```typescript
// ✅ SAFE: Using Prisma ORM
const user = await prisma.user.findUnique({
    where: { email: userInput }, // Parameterized
});

// ✅ SAFE: Using TypeORM
const users = await userRepository.find({
    where: { email: userInput }, // Parameterized
});

// ✅ SAFE: Using Sequelize
const user = await User.findOne({
    where: { email: userInput }, // Parameterized
});
```

### 1.2 Raw Queries (Parameterized)

```typescript
// ✅ SAFE: Parameterized query
const result = await db.query(
    'SELECT * FROM users WHERE email = $1',
    [userEmail] // Parameter
);

// ✅ SAFE: Named parameters
const result = await db.query(
    `SELECT * FROM users WHERE email = :email`,
    { email: userEmail }
);

// ❌ DANGEROUS: String concatenation
const result = await db.query(
    `SELECT * FROM users WHERE email = '${userEmail}'` // SQL injection!
);

// ❌ DANGEROUS: String interpolation
const query = `SELECT * FROM users WHERE email = ${userEmail}`;
```

### 1.3 Validation Before Query

```typescript
// src/utils/validation.ts
import { z } from 'zod';

export const emailSchema = z.string().email();

export function validateEmail(email: unknown): string {
    return emailSchema.parse(email); // Throws if invalid
}

// src/controllers/user.controller.ts
export async function getUserByEmail(email: unknown) {
    // Validate before using in query
    const validEmail = validateEmail(email);

    const user = await db.user.findUnique({
        where: { email: validEmail },
    });

    return user;
}
```

## 2. XSS (CROSS-SITE SCRIPTING) PREVENTION

### 2.1 Output Escaping

```typescript
// src/utils/xss.ts
import DOMPurify from 'isomorphic-dompurify';

/**
 * Sanitize HTML content
 */
export function sanitizeHTML(html: string): string {
    return DOMPurify.sanitize(html, {
        ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'a', 'p', 'br', 'ul', 'li'],
        ALLOWED_ATTR: ['href', 'title'],
    });
}

/**
 * Escape HTML entities
 */
export function escapeHTML(text: string): string {
    const map: Record<string, string> = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;',
    };
    return text.replace(/[&<>"']/g, (char) => map[char]);
}

// ✅ SAFE: Escaped output
const user = await db.user.findUnique({ where: { id: userId } });
const safeUserName = escapeHTML(user.name);

res.json({ userName: safeUserName }); // Safe
```

### 2.2 Content Security Policy

```typescript
// src/middleware/csp.ts
import helmet from 'helmet';

app.use(helmet.contentSecurityPolicy({
    directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", 'data:', 'https:'],
        connectSrc: ["'self'"],
        frameSrc: 'none',
        objectSrc: 'none',
    },
}));
```

## 3. CSRF (CROSS-SITE REQUEST FORGERY) PREVENTION

### 3.1 CSRF Token Protection

```typescript
// src/middleware/csrf.ts
import csrf from 'csurf';
import cookieParser from 'cookie-parser';

const csrfProtection = csrf({ cookie: false }); // Use session instead

// Middleware setup
app.use(cookieParser());
app.use(csrfProtection);

// Generate token for form
app.get('/form', (req, res) => {
    const token = req.csrfToken();
    res.json({ csrfToken: token });
});

// Verify token on submit
app.post('/submit', csrfProtection, (req, res) => {
    // If CSRF check fails, middleware throws error
    res.json({ success: true });
});
```

### 3.2 SameSite Cookie Protection

```typescript
// src/config/cookies.ts
app.use(session({
    // ...
    cookie: {
        httpOnly: true, // JavaScript can't access
        secure: true, // HTTPS only
        sameSite: 'strict', // Prevent CSRF
        maxAge: 24 * 60 * 60 * 1000,
    },
}));

// For API tokens
const token = jwt.sign(payload, secret);
res.cookie('accessToken', token, {
    httpOnly: true,
    secure: true,
    sameSite: 'strict',
    path: '/',
    domain: '.example.com',
});
```

## 4. RATE LIMITING & DDoS PROTECTION

### 4.1 Global Rate Limiting

```typescript
// src/middleware/rate-limit.ts
import rateLimit from 'express-rate-limit';
import RedisStore from 'rate-limit-redis';
import { redis } from '@/core/cache';

/**
 * General API rate limiter
 */
export const generalLimiter = rateLimit({
    store: new RedisStore({
        client: redis,
        prefix: 'rl:general:',
    }),
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // 100 requests per windowMs
    message: 'Too many requests',
    standardHeaders: true,
    legacyHeaders: false,
});

/**
 * Strict limiter for login
 */
export const strictLimiter = rateLimit({
    store: new RedisStore({
        client: redis,
        prefix: 'rl:strict:',
    }),
    windowMs: 15 * 60 * 1000,
    max: 5, // 5 attempts per 15 minutes
    skipSuccessfulRequests: true, // Don't count successful attempts
});

/**
 * Per-user limiter
 */
export const perUserLimiter = (max: number, windowMs: number) => {
    return rateLimit({
        store: new RedisStore({
            client: redis,
            prefix: 'rl:user:',
        }),
        windowMs,
        max,
        keyGenerator: (req) => {
            // Use user ID if authenticated, otherwise IP
            return (req as any).user?.id || req.ip;
        },
    });
};

// Usage
app.post('/auth/login', strictLimiter, authController.login);
app.use('/api/', generalLimiter);
app.get('/exports/generate', perUserLimiter(5, 3600000), exportController.generate);
```

### 4.2 Advanced DDoS Protection

```typescript
// src/middleware/ddos-protection.ts

/**
 * Detect and block DDoS attacks
 */
export async function detectDDoS(req: Request, res: Response, next: NextFunction) {
    const ip = req.ip;
    const key = `ddos:${ip}`;

    // Check if IP is blocked
    if (await cache.exists(`${key}:blocked`)) {
        res.status(429).json({ error: 'Too many requests' });
        return;
    }

    // Increment request count
    const count = await cache.incr(key);

    if (count === 1) {
        // Set expiration on first request
        await cache.expire(key, 60); // 1 minute window
    }

    // Block after threshold
    if (count > 1000) {
        await cache.setex(`${key}:blocked`, 3600, '1'); // Block for 1 hour
        res.status(429).json({ error: 'IP blocked due to DDoS' });
        return;
    }

    next();
}

app.use(detectDDoS);
```

## 5. PASSWORD SECURITY

### 5.1 Bcrypt Hashing (Recommended)

```typescript
// src/utils/password.ts
import bcrypt from 'bcryptjs';

/**
 * Hash password securely
 */
export async function hashPassword(password: string): Promise<string> {
    // Validate password strength first
    validatePasswordStrength(password);

    // Bcrypt with cost factor 12 (takes ~250ms per hash)
    return bcrypt.hash(password, 12);
}

/**
 * Verify password
 */
export async function verifyPassword(
    password: string,
    hash: string
): Promise<boolean> {
    return bcrypt.compare(password, hash);
}

/**
 * Validate password strength
 */
function validatePasswordStrength(password: string): void {
    if (password.length < 12) {
        throw new Error('Password must be at least 12 characters');
    }
    if (!password.match(/[A-Z]/)) {
        throw new Error('Must contain uppercase letter');
    }
    if (!password.match(/[a-z]/)) {
        throw new Error('Must contain lowercase letter');
    }
    if (!password.match(/[0-9]/)) {
        throw new Error('Must contain digit');
    }
    if (!password.match(/[!@#$%^&*()\-_=\[\]{};':"\\|,.<>\/?]/)) {
        throw new Error('Must contain special character');
    }
}

// Usage
const hashedPassword = await hashPassword(userPassword);
await db.user.create({
    data: {
        email,
        hashedPassword,
    },
});
```

## 6. API KEY MANAGEMENT

### 6.1 Secure API Key Handling

```typescript
// src/services/api-key.service.ts
import crypto from 'crypto';

/**
 * Generate API key
 */
export function generateAPIKey(): { prefix: string; secret: string; hash: string } {
    // Generate random bytes
    const randomBytes = crypto.randomBytes(32);
    const secret = randomBytes.toString('hex');

    // Prefix for identification
    const prefix = 'sk_' + crypto.randomBytes(4).toString('hex');

    // Hash for storage
    const hash = crypto.createHash('sha256').update(secret).digest('hex');

    return { prefix, secret, hash };
}

/**
 * Store API key in database (hash only)
 */
export async function createAPIKey(
    userId: string,
    name: string
): Promise<{ apiKey: string; secret: string }> {
    const { prefix, secret, hash } = generateAPIKey();
    const apiKey = `${prefix}_${secret}`;

    // Store only hash in database
    await db.apiKey.create({
        data: {
            userId,
            name,
            prefix,
            hashedSecret: hash,
            lastUsedAt: null,
        },
    });

    return {
        apiKey, // Return full key only once
        secret,
    };
}

/**
 * Verify API key
 */
export async function verifyAPIKey(apiKey: string): Promise<any> {
    const [prefix, secret] = apiKey.split('_');

    // Hash the provided secret
    const hash = crypto.createHash('sha256').update(secret).digest('hex');

    // Find key
    const key = await db.apiKey.findFirst({
        where: {
            prefix,
            hashedSecret: hash,
        },
        include: { user: true },
    });

    if (!key) {
        throw new UnauthorizedError('Invalid API key');
    }

    // Update last used
    await db.apiKey.update({
        where: { id: key.id },
        data: { lastUsedAt: new Date() },
    });

    return key;
}

// Middleware for API key authentication
export async function apiKeyMiddleware(
    req: Request,
    res: Response,
    next: NextFunction
) {
    const apiKey = req.headers['x-api-key'] as string;

    if (!apiKey) {
        res.status(401).json({ error: 'Missing API key' });
        return;
    }

    try {
        const key = await verifyAPIKey(apiKey);
        (req as any).user = key.user;
        (req as any).apiKey = key;
        next();
    } catch (error) {
        res.status(401).json({ error: 'Invalid API key' });
    }
}
```

## 7. DATA ENCRYPTION

### 7.1 Encryption at Rest

```typescript
// src/utils/encryption.ts
import crypto from 'crypto';

/**
 * Encrypt sensitive data
 */
export function encrypt(plaintext: string): string {
    const iv = crypto.randomBytes(16);
    const cipher = crypto.createCipheriv(
        'aes-256-gcm',
        Buffer.from(process.env.ENCRYPTION_KEY!, 'hex'),
        iv
    );

    let encrypted = cipher.update(plaintext, 'utf-8', 'hex');
    encrypted += cipher.final('hex');
    const authTag = cipher.getAuthTag();

    // Return: iv + authTag + ciphertext
    return [iv.toString('hex'), authTag.toString('hex'), encrypted].join(':');
}

/**
 * Decrypt sensitive data
 */
export function decrypt(encrypted: string): string {
    const [ivHex, authTagHex, ciphertextHex] = encrypted.split(':');
    const iv = Buffer.from(ivHex, 'hex');
    const authTag = Buffer.from(authTagHex, 'hex');
    const ciphertext = Buffer.from(ciphertextHex, 'hex');

    const decipher = crypto.createDecipheriv(
        'aes-256-gcm',
        Buffer.from(process.env.ENCRYPTION_KEY!, 'hex'),
        iv
    );

    decipher.setAuthTag(authTag);

    let plaintext = decipher.update(ciphertext, undefined, 'utf-8');
    plaintext += decipher.final('utf-8');

    return plaintext;
}

// Usage: Store encrypted SSN
const encryptedSSN = encrypt(userSSN);
await db.user.update({
    where: { id: userId },
    data: { encryptedSSN },
});

// Retrieve and decrypt
const user = await db.user.findUnique({ where: { id: userId } });
const ssn = decrypt(user.encryptedSSN);
```

## 8. CORS & ORIGIN VALIDATION

### 8.1 Secure CORS Configuration

```typescript
// src/middleware/cors.ts
app.use(cors({
    origin: function (origin, callback) {
        const allowedOrigins = process.env.ALLOWED_ORIGINS?.split(',') || [];

        if (!origin || allowedOrigins.includes(origin)) {
            callback(null, true);
        } else {
            callback(new Error('CORS not allowed'));
        }
    },
    credentials: true,
    optionsSuccessStatus: 200,
    methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
    allowedHeaders: ['Content-Type', 'Authorization'],
    exposedHeaders: ['X-Total-Count'],
    maxAge: 3600, // Pre-flight cache
}));
```

## 9. INPUT VALIDATION & SANITIZATION

### 9.1 Zod Validation Schema

```typescript
// src/models/user.model.ts
import { z } from 'zod';

export const userCreateSchema = z.object({
    email: z.string().email('Invalid email'),
    password: z
        .string()
        .min(12, 'Min 12 characters')
        .regex(/[A-Z]/, 'Need uppercase')
        .regex(/[a-z]/, 'Need lowercase')
        .regex(/[0-9]/, 'Need digit')
        .regex(/[!@#$%^&*]/, 'Need special char'),
    name: z.string().min(2).max(100),
    phone: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone'),
});

export type UserCreate = z.infer<typeof userCreateSchema>;

// Validation middleware
export const validateRequest = (schema: z.ZodSchema) => {
    return (req: Request, res: Response, next: NextFunction) => {
        try {
            req.body = schema.parse(req.body);
            next();
        } catch (error) {
            if (error instanceof z.ZodError) {
                res.status(400).json({ errors: error.errors });
            } else {
                next(error);
            }
        }
    };
};

// Usage
router.post(
    '/users',
    validateRequest(userCreateSchema),
    userController.create
);
```

This covers COMPLETE backend security hardening!