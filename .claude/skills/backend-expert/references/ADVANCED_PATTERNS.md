# ADVANCED BACKEND PATTERNS & ARCHITECTURE

## 1. MICROSERVICES ARCHITECTURE

### 1.1 Service-to-Service Communication

```typescript
// src/services/service-client.ts
import axios from 'axios';
import CircuitBreaker from 'opossum';

/**
 * Service discovery and health checks
 */
const services = {
    auth: process.env.AUTH_SERVICE_URL,
    product: process.env.PRODUCT_SERVICE_URL,
    order: process.env.ORDER_SERVICE_URL,
    payment: process.env.PAYMENT_SERVICE_URL,
};

// Circuit breaker for resilience
const breaker = new CircuitBreaker(async (fn) => fn(), {
    timeout: 3000,
    errorThresholdPercentage: 50,
    resetTimeout: 30000,
});

/**
 * Call another service with retry and circuit breaker
 */
export async function callService(
    serviceName: string,
    endpoint: string,
    method: 'GET' | 'POST' = 'GET',
    data?: any,
    retries: number = 3
): Promise<any> {
    const url = `${services[serviceName as keyof typeof services]}${endpoint}`;

    try {
        return await breaker.fire(async () => {
            let lastError;

            for (let i = 0; i < retries; i++) {
                try {
                    const response = await axios({
                        method,
                        url,
                        data,
                        timeout: 3000,
                        headers: {
                            'X-Service-Call': 'true',
                            'X-Correlation-ID': getCorrelationID(),
                        },
                    });

                    return response.data;
                } catch (error) {
                    lastError = error;

                    // Exponential backoff
                    if (i < retries - 1) {
                        await sleep(Math.pow(2, i) * 100);
                    }
                }
            }

            throw lastError;
        });
    } catch (error) {
        throw new ServiceUnavailableError(
            `Service ${serviceName} is unavailable`
        );
    }
}

/**
 * Saga pattern for distributed transactions
 */
export async function createOrderWithSaga(
    userId: string,
    items: OrderItem[]
): Promise<Order> {
    const orderId = generateID();
    const sagaID = generateID();

    try {
        // Step 1: Reserve inventory
        await callService('product', '/reserve', 'POST', {
            orderId,
            items,
        });

        // Step 2: Process payment
        const paymentResult = await callService('payment', '/charge', 'POST', {
            orderId,
            amount: calculateTotal(items),
        });

        if (!paymentResult.success) {
            // Compensating transaction
            await callService('product', '/release', 'POST', { orderId });
            throw new PaymentFailedError();
        }

        // Step 3: Create order
        const order = await db.order.create({
            data: {
                id: orderId,
                userId,
                items,
                paymentId: paymentResult.paymentId,
                status: 'confirmed',
            },
        });

        // Step 4: Send notification
        await callService('notification', '/send', 'POST', {
            userId,
            type: 'order_confirmed',
            orderId,
        });

        return order;
    } catch (error) {
        // Compensating transactions on failure
        await callService('product', '/release', 'POST', { orderId });
        throw error;
    }
}
```

### 1.2 Event-Driven Architecture

```typescript
// src/events/event-bus.ts
import { EventEmitter } from 'events';

class EventBus extends EventEmitter {
    async publish(event: string, data: any) {
        // Log event
        await logEvent(event, data);

        // Emit locally
        this.emit(event, data);

        // Publish to message queue (Kafka, RabbitMQ, Redis)
        await messageQueue.publish(event, data);
    }

    subscribe(event: string, handler: (data: any) => Promise<void>) {
        this.on(event, async (data) => {
            try {
                await handler(data);
            } catch (error) {
                console.error(`Error handling event ${event}:`, error);
                // Retry logic or dead letter queue
            }
        });
    }
}

export const eventBus = new EventBus();

// src/events/order.events.ts
export const OrderEvents = {
    CREATED: 'order.created',
    PAID: 'order.paid',
    SHIPPED: 'order.shipped',
    DELIVERED: 'order.delivered',
    CANCELLED: 'order.cancelled',
};

// src/services/order.service.ts
export async function createOrder(userId: string, items: OrderItem[]) {
    const order = await db.order.create({
        data: { userId, items, status: 'pending' },
    });

    // Publish event
    await eventBus.publish(OrderEvents.CREATED, {
        orderId: order.id,
        userId,
        items,
        createdAt: new Date(),
    });

    return order;
}

// src/listeners/order.listeners.ts
eventBus.subscribe(OrderEvents.CREATED, async (data) => {
    // Send confirmation email
    await emailService.sendOrderConfirmation(data.userId, data.orderId);
});

eventBus.subscribe(OrderEvents.CREATED, async (data) => {
    // Create analytics event
    await analytics.track('order_created', data);
});

eventBus.subscribe(OrderEvents.CREATED, async (data) => {
    // Schedule order expiry timer
    await scheduleOrderExpiry(data.orderId, 24 * 60 * 60 * 1000); // 24 hours
});
```

## 2. CQRS PATTERN (Command Query Responsibility Segregation)

```typescript
// src/cqrs/commands.ts
/**
 * Commands: Changes system state (write operations)
 */
export class CreateUserCommand {
    constructor(
        public email: string,
        public password: string,
        public name: string
    ) {}
}

export class UpdateUserCommand {
    constructor(
        public userId: string,
        public data: Partial<User>
    ) {}
}

export class DeleteUserCommand {
    constructor(public userId: string) {}
}

// src/cqrs/command-handler.ts
export class CreateUserCommandHandler {
    async execute(command: CreateUserCommand): Promise<User> {
        // Validate
        if (await db.user.findUnique({ where: { email: command.email } })) {
            throw new ConflictError('Email already exists');
        }

        // Create
        const user = await db.user.create({
            data: {
                email: command.email,
                hashedPassword: await hashPassword(command.password),
                name: command.name,
            },
        });

        // Publish event
        await eventBus.publish(UserEvents.CREATED, {
            userId: user.id,
            email: user.email,
        });

        return user;
    }
}

// src/cqrs/queries.ts
/**
 * Queries: Read system state (no side effects)
 */
export class GetUserQuery {
    constructor(public userId: string) {}
}

export class GetUsersQuery {
    constructor(
        public page: number = 1,
        public limit: number = 20,
        public role?: string
    ) {}
}

// src/cqrs/query-handler.ts
export class GetUserQueryHandler {
    async execute(query: GetUserQuery): Promise<User | null> {
        // Use read replica or cache
        return getOrCache(
            `user:${query.userId}`,
            3600,
            () => db.userReadReplica.findUnique({ where: { id: query.userId } })
        );
    }
}

// src/cqrs/bus.ts
class CommandBus {
    private handlers = new Map();

    register(commandType: Function, handler: any) {
        this.handlers.set(commandType, handler);
    }

    async execute(command: any) {
        const handler = this.handlers.get(command.constructor);

        if (!handler) {
            throw new Error(`No handler for ${command.constructor.name}`);
        }

        return await handler.execute(command);
    }
}

class QueryBus {
    private handlers = new Map();

    register(queryType: Function, handler: any) {
        this.handlers.set(queryType, handler);
    }

    async execute(query: any) {
        const handler = this.handlers.get(query.constructor);

        if (!handler) {
            throw new Error(`No handler for ${query.constructor.name}`);
        }

        return await handler.execute(query);
    }
}

export const commandBus = new CommandBus();
export const queryBus = new QueryBus();

// Register handlers
commandBus.register(CreateUserCommand, new CreateUserCommandHandler());
queryBus.register(GetUserQuery, new GetUserQueryHandler());

// Usage in controllers
export async function createUser(req: Request, res: Response) {
    const command = new CreateUserCommand(
        req.body.email,
        req.body.password,
        req.body.name
    );

    const user = await commandBus.execute(command);
    res.json(user);
}

export async function getUser(req: Request, res: Response) {
    const query = new GetUserQuery(req.params.id);
    const user = await queryBus.execute(query);
    res.json(user);
}
```

## 3. MESSAGE QUEUE INTEGRATION

### 3.1 Bull (Node.js Job Queue)

```typescript
// src/queue/queue.ts
import Queue from 'bull';

export const emailQueue = new Queue('email', process.env.REDIS_URL);
export const paymentQueue = new Queue('payment', process.env.REDIS_URL);
export const reportQueue = new Queue('report', process.env.REDIS_URL);

/**
 * Process email jobs
 */
emailQueue.process(async (job) => {
    const { email, template, data } = job.data;

    try {
        await emailService.send(email, template, data);
        return { success: true };
    } catch (error) {
        // Will retry automatically
        throw error;
    }
});

// On success
emailQueue.on('completed', (job) => {
    console.log(`Email job ${job.id} completed`);
});

// On failure
emailQueue.on('failed', (job, err) => {
    console.error(`Email job ${job.id} failed:`, err.message);
});

/**
 * Add job to queue
 */
export async function sendEmailAsync(
    email: string,
    template: string,
    data: any
) {
    await emailQueue.add(
        { email, template, data },
        {
            priority: 5,
            attempts: 3, // Retry 3 times
            backoff: {
                type: 'exponential',
                delay: 2000,
            },
            removeOnComplete: true,
        }
    );
}

/**
 * Process payment jobs
 */
paymentQueue.process(async (job) => {
    const { orderId, amount } = job.data;

    const result = await paymentService.charge(orderId, amount);

    if (!result.success) {
        throw new PaymentFailedError(result.message);
    }

    return result;
});

/**
 * Add payment job
 */
export async function processPaymentAsync(orderId: string, amount: number) {
    const job = await paymentQueue.add(
        { orderId, amount },
        {
            priority: 10, // High priority
            attempts: 2,
            delay: 1000,
        }
    );

    return job.id;
}
```

### 3.2 Kafka Integration

```typescript
// src/queue/kafka.ts
import { Kafka, Producer, Consumer } from 'kafkajs';

const kafka = new Kafka({
    clientId: 'order-service',
    brokers: (process.env.KAFKA_BROKERS || 'localhost:9092').split(','),
});

export const producer = kafka.producer({
    allowAutoTopicCreation: false,
    transactionTimeout: 30000,
});

export const consumer = kafka.consumer({ groupId: 'order-service-group' });

/**
 * Publish event to Kafka
 */
export async function publishEvent(
    topic: string,
    data: any,
    key?: string
) {
    await producer.send({
        topic,
        messages: [
            {
                key,
                value: JSON.stringify(data),
                headers: {
                    'correlation-id': getCorrelationID(),
                    'timestamp': new Date().toISOString(),
                },
            },
        ],
    });
}

/**
 * Consume events from Kafka
 */
export async function subscribeToTopic(
    topic: string,
    handler: (data: any) => Promise<void>
) {
    await consumer.subscribe({ topic });

    await consumer.run({
        eachMessage: async ({ topic, partition, message }) => {
            try {
                const data = JSON.parse(message.value.toString());
                await handler(data);
            } catch (error) {
                console.error(`Error processing message from ${topic}:`, error);
                // Send to dead letter queue
                await publishEvent(`${topic}.dlq`, message.value);
            }
        },
    });
}

// Usage
await publishEvent('order.created', {
    orderId: order.id,
    userId: order.userId,
    items: order.items,
});

await subscribeToTopic('order.paid', async (data) => {
    await orderService.markAsPaid(data.orderId);
});
```

## 4. DEPENDENCY INJECTION

```typescript
// src/container.ts
import { Container } from 'inversify';
import 'reflect-metadata';

export const container = new Container();

// Register services
container.bind('UserRepository').to(UserRepository);
container.bind('UserService').to(UserService);
container.bind('AuthService').to(AuthService);
container.bind('EmailService').to(EmailService);

// src/services/user.service.ts
import { injectable, inject } from 'inversify';

@injectable()
export class UserService {
    constructor(
        @inject('UserRepository') private userRepository: UserRepository,
        @inject('EmailService') private emailService: EmailService
    ) {}

    async createUser(email: string, password: string) {
        const user = await this.userRepository.create({
            email,
            hashedPassword: await hashPassword(password),
        });

        await this.emailService.sendWelcomeEmail(email);

        return user;
    }
}

// src/controllers/user.controller.ts
@injectable()
export class UserController {
    constructor(@inject('UserService') private userService: UserService) {}

    async create(req: Request, res: Response) {
        const user = await this.userService.createUser(
            req.body.email,
            req.body.password
        );
        res.json(user);
    }
}
```

This covers COMPLETE advanced backend patterns!