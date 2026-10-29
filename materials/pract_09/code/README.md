# Transactions and Indexes with Docker

## Запуск

```bash
docker-compose up -d
docker exec -it webprog_transactions_db psql -U webprog -d webprog
```

## Примеры

- `transactions.py` - базовые транзакции (перевод, гонки, блокировки)
- `indexes.py` - базовые индексы (создание, EXPLAIN, N+1)
- `advanced_transactions.py` - deadlock, savepoints, isolation levels
- `advanced_indexes.py` - partial, functional, covering indexes

## Описание

**transactions.py:** Connection pooling, атомарность, SELECT FOR UPDATE, UNIQUE constraint

**indexes.py:** Создание индексов, EXPLAIN ANALYZE, Seq Scan vs Index Scan, N+1 проблема

**advanced_transactions.py:** Deadlock detection, savepoints, isolation levels, transaction monitoring

**advanced_indexes.py:** Partial indexes, functional indexes, covering indexes, index statistics, REINDEX, VACUUM

## Docker CLI

```bash
# Транзакции
BEGIN; UPDATE accounts SET balance = balance - 100 WHERE id = 1; COMMIT;
SELECT pid, state, query FROM pg_stat_activity WHERE state = 'active';

# Индексы
CREATE INDEX idx_users_email ON users(email);
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'user@example.com';
SELECT indexname, idx_scan FROM pg_stat_user_indexes;
```

## Когда использовать

**Транзакции:** Всегда для связанных операций, SELECT FOR UPDATE для критических обновлений

**Индексы:** Частые WHERE, составные для нескольких колонок, partial для фильтруемых данных
