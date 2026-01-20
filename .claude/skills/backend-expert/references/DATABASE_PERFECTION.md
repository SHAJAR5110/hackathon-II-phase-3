# ULTIMATE DATABASE PATTERNS & OPTIMIZATION

## 1. POSTGRESQL SETUP & OPTIMIZATION

### 1.1 Connection Pooling (Critical)

```typescript
// src/core/database.ts
import { Pool, Client } from 'pg';

/**
 * Create connection pool (PERFECTION)
 * Reuses connections instead of creating new ones
 */
export const pool = new Pool({
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME,
    user: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    // Connection pool settings
    max: 20, // Max clients in pool
    idleTimeoutMillis: 30000, // Close idle after 30s
    connectionTimeoutMillis: 2000, // Timeout for new connection
});

// Monitor pool
pool.on('error', (err) => {
    console.error('Unexpected error on idle client', err);
});

pool.on('connect', () => {
    console.log('New client connected to database');
});

export async function query(text: string, values?: any[]) {
    const start = Date.now();
    try {
        const res = await pool.query(text, values);
        const duration = Date.now() - start;

        // Log slow queries
        if (duration > 1000) {
            console.warn('Slow query', {
                text,
                duration,
                rows: res.rowCount,
            });
        }

        return res;
    } catch (error) {
        console.error('Database query error', {
            text,
            error: error instanceof Error ? error.message : error,
        });
        throw error;
    }
}

export async function getClient() {
    return pool.connect();
}
```

### 1.2 Database Schema with Indexes

```sql
-- Users table with indexes
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashedPassword VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    role_id UUID REFERENCES roles(id),
    emailVerified BOOLEAN DEFAULT false,
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW(),
    INDEX idx_users_email (email),
    INDEX idx_users_role_id (role_id),
    INDEX idx_users_createdAt (createdAt DESC)
);

-- Orders table with proper indexes
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending', -- pending, processing, shipped, delivered
    totalAmount DECIMAL(10, 2) NOT NULL,
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW(),
    INDEX idx_orders_user_id (user_id),
    INDEX idx_orders_status (status),
    INDEX idx_orders_createdAt (createdAt DESC),
    INDEX idx_orders_user_status (user_id, status) -- Composite index
);

-- Products table
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INT DEFAULT 0,
    category_id UUID REFERENCES categories(id),
    createdAt TIMESTAMP DEFAULT NOW(),
    updatedAt TIMESTAMP DEFAULT NOW(),
    INDEX idx_products_sku (sku),
    INDEX idx_products_category_id (category_id),
    INDEX idx_products_price (price),
    FULLTEXT INDEX idx_products_search (name, description) -- Full-text search
);

-- Audit log table
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(100) NOT NULL,
    resourceId VARCHAR(50),
    changes JSONB,
    ipAddress VARCHAR(45),
    timestamp TIMESTAMP DEFAULT NOW(),
    INDEX idx_audit_user_id (user_id),
    INDEX idx_audit_resource (resource, resourceId),
    INDEX idx_audit_timestamp (timestamp DESC)
);
```

### 1.3 Query Optimization

```typescript
// src/repositories/user.repository.ts

/**
 * Get user with minimal data (SELECT specific columns)
 * PERFECTION: Don't SELECT *
 */
export async function getUserSummary(userId: string) {
    return await db.query(
        `SELECT id, email, name, role_id FROM users WHERE id = $1`,
        [userId]
    );
}

/**
 * Get users with pagination
 * PERFECTION: Always paginate large result sets
 */
export async function listUsers(
    page: number = 1,
    limit: number = 20,
    role?: string
) {
    const offset = (page - 1) * limit;

    let query = 'SELECT id, email, name, role_id FROM users';
    const params: any[] = [];

    if (role) {
        query += ' WHERE role_id = (SELECT id FROM roles WHERE name = $1)';
        params.push(role);
    }

    // Add ORDER BY and pagination
    query += ` ORDER BY createdAt DESC LIMIT $${params.length + 1} OFFSET $${params.length + 2}`;
    params.push(limit, offset);

    const [result, countResult] = await Promise.all([
        db.query(query, params),
        db.query(
            `SELECT COUNT(*) as total FROM users${role ? ' WHERE role_id = (SELECT id FROM roles WHERE name = $1)' : ''}`,
            role ? [role] : []
        ),
    ]);

    return {
        users: result.rows,
        total: parseInt(countResult.rows[0].total),
        page,
        limit,
        pages: Math.ceil(countResult.rows[0].total / limit),
    };
}

/**
 * Batch insert (more efficient than individual inserts)
 */
export async function insertBatch(
    items: Array<{ email: string; name: string }>
) {
    const placeholders = items
        .map((_, i) => `($${i * 2 + 1}, $${i * 2 + 2})`)
        .join(', ');
    const values = items.flatMap((item) => [item.email, item.name]);

    return await db.query(
        `INSERT INTO users (email, name) VALUES ${placeholders}`,
        values
    );
}

/**
 * Use EXPLAIN to analyze query performance
 */
export async function analyzeQuery(sql: string) {
    const result = await db.query(`EXPLAIN ANALYZE ${sql}`);
    console.log('Query plan:', result.rows);
}
```

## 2. MONGODB PATTERNS

### 2.1 Connection & Indexing

```typescript
// src/core/mongodb.ts
import { MongoClient, Db } from 'mongodb';

let db: Db;

export async function connectMongoDB(): Promise<Db> {
    const client = new MongoClient(process.env.MONGODB_URI!);

    await client.connect();
    db = client.db(process.env.MONGODB_DB);

    // Create indexes
    await createIndexes();

    return db;
}

async function createIndexes() {
    // Users collection
    await db.collection('users').createIndex({ email: 1 }, { unique: true });
    await db.collection('users').createIndex({ createdAt: -1 });

    // Orders collection
    await db.collection('orders').createIndex({ userId: 1, createdAt: -1 });
    await db.collection('orders').createIndex({ status: 1 });

    // Products collection
    await db.collection('products').createIndex(
        { name: 'text', description: 'text' }, // Full-text search
        { default_language: 'english' }
    );
    await db.collection('products').createIndex({ sku: 1 }, { unique: true });
}

export function getDB(): Db {
    return db;
}
```

### 2.2 MongoDB Queries

```typescript
// src/repositories/order.repository.ts

/**
 * Find orders with aggregation pipeline (efficient)
 */
export async function getOrdersWithDetails(userId: string) {
    const db = getDB();

    return await db.collection('orders').aggregate([
        // Stage 1: Match user orders
        { $match: { userId: new ObjectId(userId) } },

        // Stage 2: Lookup product details
        {
            $lookup: {
                from: 'products',
                localField: 'productIds',
                foreignField: '_id',
                as: 'products',
            },
        },

        // Stage 3: Lookup user details
        {
            $lookup: {
                from: 'users',
                localField: 'userId',
                foreignField: '_id',
                as: 'user',
            },
        },

        // Stage 4: Unwind (flatten) user array
        { $unwind: '$user' },

        // Stage 5: Project (select fields)
        {
            $project: {
                _id: 1,
                status: 1,
                totalAmount: 1,
                createdAt: 1,
                'user.name': 1,
                'user.email': 1,
                'products.name': 1,
                'products.price': 1,
            },
        },

        // Stage 6: Sort
        { $sort: { createdAt: -1 } },

        // Stage 7: Pagination
        { $skip: 0 },
        { $limit: 20 },
    ]).toArray();
}

/**
 * Bulk write operations (efficient)
 */
export async function bulkUpdateProducts(updates: Array<{ _id: string; stock: number }>) {
    const db = getDB();

    const operations = updates.map((update) => ({
        updateOne: {
            filter: { _id: new ObjectId(update._id) },
            update: { $set: { stock: update.stock, updatedAt: new Date() } },
        },
    }));

    return await db.collection('products').bulkWrite(operations);
}
```

## 3. REDIS CACHING

### 3.1 Redis Setup & Patterns

```typescript
// src/core/cache.ts
import Redis from 'ioredis';

export const redis = new Redis({
    host: process.env.REDIS_HOST || 'localhost',
    port: parseInt(process.env.REDIS_PORT || '6379'),
    password: process.env.REDIS_PASSWORD,
    maxRetriesPerRequest: null,
    enableReadyCheck: false,
    retryStrategy: (times) => {
        const delay = Math.min(times * 50, 2000);
        return delay;
    },
});

/**
 * Cache-aside pattern
 */
export async function getOrCache<T>(
    key: string,
    ttl: number,
    fetchFn: () => Promise<T>
): Promise<T> {
    // Try to get from cache
    const cached = await redis.get(key);

    if (cached) {
        return JSON.parse(cached) as T;
    }

    // Fetch data
    const data = await fetchFn();

    // Store in cache
    await redis.setex(key, ttl, JSON.stringify(data));

    return data;
}

/**
 * Get user with caching
 */
export async function getCachedUser(userId: string) {
    return getOrCache(
        `user:${userId}`,
        3600, // 1 hour TTL
        () => db.user.findUnique({ where: { id: userId } })
    );
}

/**
 * Invalidate cache
 */
export async function invalidateUserCache(userId: string) {
    await redis.del(`user:${userId}`);
}

/**
 * Batch cache operations
 */
export async function getOrCacheBatch<T>(
    keys: string[],
    ttl: number,
    fetchFn: (missingKeys: string[]) => Promise<Record<string, T>>
): Promise<Record<string, T>> {
    // Get all from cache
    const cached = await redis.mget(...keys);

    const result: Record<string, T> = {};
    const missingKeys: string[] = [];

    // Check which keys are missing
    keys.forEach((key, index) => {
        if (cached[index]) {
            result[key] = JSON.parse(cached[index]);
        } else {
            missingKeys.push(key);
        }
    });

    // Fetch missing data
    if (missingKeys.length > 0) {
        const freshData = await fetchFn(missingKeys);

        // Cache and add to result
        const pipeline = redis.pipeline();

        Object.entries(freshData).forEach(([key, data]) => {
            result[key] = data;
            pipeline.setex(key, ttl, JSON.stringify(data));
        });

        await pipeline.exec();
    }

    return result;
}
```

### 3.2 Rate Limiting with Redis

```typescript
// src/middleware/rate-limit.ts

/**
 * Token bucket algorithm
 */
export async function isRateLimited(
    key: string,
    maxRequests: number,
    windowSeconds: number
): Promise<boolean> {
    const current = await redis.incr(key);

    if (current === 1) {
        await redis.expire(key, windowSeconds);
    }

    return current > maxRequests;
}

/**
 * Sliding window counter
 */
export async function checkSlidingWindow(
    key: string,
    maxRequests: number,
    windowSeconds: number
): Promise<boolean> {
    const now = Date.now();
    const windowStart = now - windowSeconds * 1000;

    // Remove old entries
    await redis.zremrangebyscore(key, '-inf', windowStart);

    // Count requests in window
    const count = await redis.zcard(key);

    if (count >= maxRequests) {
        return true; // Rate limited
    }

    // Add current request
    await redis.zadd(key, now, `${now}-${Math.random()}`);
    await redis.expire(key, windowSeconds + 1);

    return false; // Not rate limited
}
```

## 4. ELASTICSEARCH INTEGRATION

### 4.1 Full-Text Search Setup

```typescript
// src/core/elasticsearch.ts
import { Client } from '@elastic/elasticsearch';

export const elasticsearch = new Client({
    node: process.env.ELASTICSEARCH_URL || 'http://localhost:9200',
});

/**
 * Create index with mappings
 */
export async function createProductIndex() {
    await elasticsearch.indices.create({
        index: 'products',
        settings: {
            number_of_shards: 1,
            number_of_replicas: 1,
        },
        mappings: {
            properties: {
                name: {
                    type: 'text',
                    analyzer: 'standard',
                    fields: {
                        keyword: { type: 'keyword' },
                    },
                },
                description: {
                    type: 'text',
                    analyzer: 'standard',
                },
                price: { type: 'double' },
                category: { type: 'keyword' },
                sku: { type: 'keyword' },
                stock: { type: 'integer' },
                createdAt: { type: 'date' },
            },
        },
    });
}

/**
 * Index product
 */
export async function indexProduct(product: any) {
    await elasticsearch.index({
        index: 'products',
        id: product.id,
        body: {
            name: product.name,
            description: product.description,
            price: product.price,
            category: product.category,
            sku: product.sku,
            stock: product.stock,
            createdAt: product.createdAt,
        },
    });
}

/**
 * Search products
 */
export async function searchProducts(query: string, filters?: any) {
    return await elasticsearch.search({
        index: 'products',
        body: {
            query: {
                bool: {
                    must: [
                        {
                            multi_match: {
                                query,
                                fields: ['name^2', 'description'],
                            },
                        },
                    ],
                    filter: filters ? Object.entries(filters).map(([key, value]) => ({
                        term: { [key]: value },
                    })) : [],
                },
            },
            sort: [{ _score: { order: 'desc' } }],
            from: 0,
            size: 20,
        },
    });
}
```

This covers COMPLETE database patterns and optimization!