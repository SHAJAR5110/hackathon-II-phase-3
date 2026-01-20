# TESTING & DEPLOYMENT MASTERY

## 1. UNIT TESTING (Jest)

### 1.1 Service Testing

```typescript
// src/services/__tests__/user.service.test.ts
import { UserService } from '../user.service';
import { UserRepository } from '../../repositories/user.repository';
import { EmailService } from '../email.service';

describe('UserService', () => {
    let userService: UserService;
    let userRepository: jest.Mocked<UserRepository>;
    let emailService: jest.Mocked<EmailService>;

    beforeEach(() => {
        userRepository = {
            create: jest.fn(),
            findByEmail: jest.fn(),
            update: jest.fn(),
        } as any;

        emailService = {
            sendWelcomeEmail: jest.fn(),
        } as any;

        userService = new UserService(userRepository, emailService);
    });

    describe('createUser', () => {
        it('should create user with hashed password', async () => {
            const userData = {
                email: 'test@example.com',
                password: 'Password123!',
                name: 'Test User',
            };

            userRepository.create.mockResolvedValue({
                id: '123',
                ...userData,
                hashedPassword: '$2b$12$...',
            });

            const result = await userService.createUser(
                userData.email,
                userData.password,
                userData.name
            );

            expect(result.email).toBe(userData.email);
            expect(userRepository.create).toHaveBeenCalled();
            expect(emailService.sendWelcomeEmail).toHaveBeenCalledWith(
                userData.email
            );
        });

        it('should throw error if email already exists', async () => {
            const email = 'existing@example.com';

            userRepository.findByEmail.mockResolvedValue({
                id: '456',
                email,
            } as any);

            await expect(
                userService.createUser(email, 'Password123!', 'User')
            ).rejects.toThrow('Email already exists');
        });

        it('should validate password strength', async () => {
            await expect(
                userService.createUser(
                    'test@example.com',
                    'weak', // Too weak
                    'User'
                )
            ).rejects.toThrow('Password must be at least 12 characters');
        });
    });

    describe('updateUser', () => {
        it('should update user data', async () => {
            const userId = '123';
            const updateData = { name: 'New Name' };

            userRepository.update.mockResolvedValue({
                id: userId,
                ...updateData,
            } as any);

            const result = await userService.updateUser(userId, updateData);

            expect(result.name).toBe(updateData.name);
            expect(userRepository.update).toHaveBeenCalledWith(userId, updateData);
        });
    });
});
```

### 1.2 Authentication Testing

```typescript
// src/services/__tests__/auth.service.test.ts
describe('AuthService', () => {
    describe('login', () => {
        it('should return tokens on successful login', async () => {
            const credentials = {
                email: 'test@example.com',
                password: 'Password123!',
            };

            userRepository.findByEmail.mockResolvedValue({
                id: 'user123',
                email: credentials.email,
                hashedPassword: await hashPassword(credentials.password),
                mfaEnabled: false,
            } as any);

            const result = await authService.login(
                credentials.email,
                credentials.password,
                '127.0.0.1'
            );

            expect(result.accessToken).toBeDefined();
            expect(result.refreshToken).toBeDefined();
            expect(result.user.id).toBe('user123');
        });

        it('should lock account after 5 failed attempts', async () => {
            const email = 'test@example.com';

            userRepository.findByEmail.mockResolvedValue({
                id: 'user123',
                email,
                hashedPassword: await hashPassword('CorrectPassword123!'),
                failedLoginAttempts: 4,
            } as any);

            // 5th failed attempt
            await expect(
                authService.login(email, 'WrongPassword', '127.0.0.1')
            ).rejects.toThrow('Too many failed attempts. Account locked.');

            expect(userRepository.update).toHaveBeenCalledWith('user123', {
                isLocked: true,
            });
        });
    });
});
```

## 2. INTEGRATION TESTING

### 2.1 API Integration Tests

```typescript
// src/__tests__/integration/auth.integration.test.ts
import request from 'supertest';
import app from '../../main';
import { db } from '../../core/database';

describe('Auth API', () => {
    beforeEach(async () => {
        // Clear database before each test
        await db.user.deleteMany({});
    });

    afterAll(async () => {
        await db.$disconnect();
    });

    describe('POST /api/auth/register', () => {
        it('should register new user', async () => {
            const userData = {
                email: 'newuser@example.com',
                password: 'Password123!',
                name: 'New User',
            };

            const response = await request(app)
                .post('/api/auth/register')
                .send(userData)
                .expect(201);

            expect(response.body.user.email).toBe(userData.email);
            expect(response.body.user.id).toBeDefined();
            expect(response.body.accessToken).toBeDefined();

            // Verify user in database
            const user = await db.user.findUnique({
                where: { email: userData.email },
            });
            expect(user).toBeDefined();
        });

        it('should reject duplicate email', async () => {
            const userData = {
                email: 'user@example.com',
                password: 'Password123!',
                name: 'User',
            };

            // Register first time
            await request(app)
                .post('/api/auth/register')
                .send(userData)
                .expect(201);

            // Try to register again
            await request(app)
                .post('/api/auth/register')
                .send(userData)
                .expect(409);
        });

        it('should validate password strength', async () => {
            const response = await request(app)
                .post('/api/auth/register')
                .send({
                    email: 'user@example.com',
                    password: 'weak',
                    name: 'User',
                })
                .expect(400);

            expect(response.body.error).toContain('password');
        });
    });

    describe('POST /api/auth/login', () => {
        beforeEach(async () => {
            // Create a test user
            await request(app)
                .post('/api/auth/register')
                .send({
                    email: 'user@example.com',
                    password: 'Password123!',
                    name: 'User',
                });
        });

        it('should login with correct credentials', async () => {
            const response = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'user@example.com',
                    password: 'Password123!',
                })
                .expect(200);

            expect(response.body.accessToken).toBeDefined();
            expect(response.body.user.email).toBe('user@example.com');
        });

        it('should reject invalid credentials', async () => {
            await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'user@example.com',
                    password: 'WrongPassword',
                })
                .expect(401);
        });
    });

    describe('Protected endpoints', () => {
        let accessToken: string;

        beforeEach(async () => {
            const response = await request(app)
                .post('/api/auth/register')
                .send({
                    email: 'user@example.com',
                    password: 'Password123!',
                    name: 'User',
                });

            accessToken = response.body.accessToken;
        });

        it('should access protected endpoint with token', async () => {
            await request(app)
                .get('/api/users/me')
                .set('Authorization', `Bearer ${accessToken}`)
                .expect(200);
        });

        it('should reject without token', async () => {
            await request(app)
                .get('/api/users/me')
                .expect(401);
        });

        it('should reject with invalid token', async () => {
            await request(app)
                .get('/api/users/me')
                .set('Authorization', 'Bearer invalid_token')
                .expect(401);
        });
    });
});
```

## 3. LOAD TESTING

### 3.1 Artillery Load Testing

```yaml
# artillery-config.yml
config:
  target: http://localhost:3000
  phases:
    - duration: 60
      arrivalRate: 10 # 10 requests/sec
      rampTo: 50 # Increase to 50/sec
      name: Ramp up
    - duration: 300
      arrivalRate: 50
      name: Sustained load
    - duration: 60
      arrivalRate: 50
      rampTo: 0
      name: Ramp down

scenarios:
  - name: User Journey
    flow:
      # Register
      - post:
          url: /api/auth/register
          json:
            email: "{{ $randomString() }}@example.com"
            password: Password123!
            name: Test User
          capture:
            - json: $.accessToken
              as: accessToken
      
      # Login (next iteration)
      - post:
          url: /api/auth/login
          json:
            email: "{{ $randomString() }}@example.com"
            password: Password123!
          capture:
            - json: $.accessToken
              as: accessToken
      
      # Get profile
      - get:
          url: /api/users/me
          headers:
            Authorization: Bearer {{ accessToken }}
      
      # Update profile
      - patch:
          url: /api/users/me
          json:
            name: Updated Name
          headers:
            Authorization: Bearer {{ accessToken }}
      
      # Create product (admin only)
      - post:
          url: /api/products
          json:
            name: Product Name
            price: 99.99
            stock: 100
          headers:
            Authorization: Bearer {{ accessToken }}
```

### 3.2 K6 Performance Testing

```typescript
// load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 }, // Ramp up
        { duration: '1m30s', target: 50 }, // Stay at 50
        { duration: '30s', target: 0 }, // Ramp down
    ],
};

export default function () {
    // Test login endpoint
    const loginRes = http.post(
        'http://localhost:3000/api/auth/login',
        JSON.stringify({
            email: 'test@example.com',
            password: 'Password123!',
        }),
        {
            headers: { 'Content-Type': 'application/json' },
        }
    );

    check(loginRes, {
        'login success': (r) => r.status === 200,
        'has accessToken': (r) =>
            r.json().accessToken !== undefined,
    });

    const token = loginRes.json().accessToken;

    // Test protected endpoint
    const meRes = http.get(
        'http://localhost:3000/api/users/me',
        {
            headers: {
                Authorization: `Bearer ${token}`,
            },
        }
    );

    check(meRes, {
        'get profile success': (r) => r.status === 200,
        'profile has email': (r) =>
            r.json().email !== undefined,
    });

    sleep(1); // Think time
}
```

## 4. DOCKER & KUBERNETES DEPLOYMENT

### 4.1 Dockerfile (Production-Grade)

```dockerfile
# Dockerfile

# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Remove devDependencies
RUN npm ci --only=production

# Runtime stage
FROM node:18-alpine

WORKDIR /app

# Install dumb-init (to handle signals properly)
RUN apk add --no-cache dumb-init

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy from builder
COPY --from=builder --chown=nodejs:nodejs /app/node_modules ./node_modules
COPY --from=builder --chown=nodejs:nodejs /app/dist ./dist
COPY --from=builder --chown=nodejs:nodejs /app/package*.json ./

# Switch to non-root user
USER nodejs

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Use dumb-init as entrypoint
ENTRYPOINT ["dumb-init", "--"]

# Start app
CMD ["node", "dist/main.js"]
```

### 4.2 Kubernetes Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: default
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  selector:
    matchLabels:
      app: backend-api
  template:
    metadata:
      labels:
        app: backend-api
        version: v1
    spec:
      serviceAccountName: backend-api
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
      containers:
        - name: api
          image: my-registry/backend-api:latest
          imagePullPolicy: Always
          ports:
            - name: http
              containerPort: 3000
              protocol: TCP
          env:
            - name: NODE_ENV
              value: production
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: database-url
            - name: JWT_SECRET
              valueFrom:
                secretKeyRef:
                  name: backend-secrets
                  key: jwt-secret
          resources:
            requests:
              cpu: 100m
              memory: 256Mi
            limits:
              cpu: 500m
              memory: 512Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 3000
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /ready
              port: 3000
            initialDelaySeconds: 10
            periodSeconds: 5
            timeoutSeconds: 3
            failureThreshold: 2
          securityContext:
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop:
                - ALL
          volumeMounts:
            - name: tmp
              mountPath: /tmp
      volumes:
        - name: tmp
          emptyDir: {}
---
apiVersion: v1
kind: Service
metadata:
  name: backend-api
spec:
  type: LoadBalancer
  selector:
    app: backend-api
  ports:
    - port: 80
      targetPort: 3000
      protocol: TCP
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-api
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: 80
```

### 4.3 GitHub Actions CI/CD

```yaml
# .github/workflows/deploy.yml
name: Deploy Backend

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
      - uses: actions/checkout@v3

      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Run tests
        run: npm run test:coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage/lcov.info

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build and push Docker image
        run: |
          docker build -t my-registry/backend-api:${{ github.sha }} .
          docker push my-registry/backend-api:${{ github.sha }}

      - name: Deploy to Kubernetes
        run: |
          kubectl set image deployment/backend-api \
            api=my-registry/backend-api:${{ github.sha }}

      - name: Verify deployment
        run: |
          kubectl rollout status deployment/backend-api
```

This covers COMPLETE testing and deployment!