#!/usr/bin/env python3
"""
XynPOS Go Service Scaffolder
Generates a complete Go microservice skeleton following XynPOS clean architecture.

Usage:
    python scripts/scaffold_service.py <service-name> <entity-name> [output-dir]
    
Examples:
    python scripts/scaffold_service.py promotion-service promotion
    python scripts/scaffold_service.py kds-service order /tmp/output
"""

import sys
import os
from pathlib import Path

def to_pascal(s: str) -> str:
    return ''.join(word.title() for word in s.replace('-', '_').split('_'))

def to_camel(s: str) -> str:
    parts = s.replace('-', '_').split('_')
    return parts[0] + ''.join(w.title() for w in parts[1:])

def scaffold(service_name: str, entity_name: str, output_dir: str):
    pascal = to_pascal(entity_name)
    camel = to_camel(entity_name)
    pkg = service_name.replace('-', '_')
    
    base = Path(output_dir) / service_name
    
    files = {
        "cmd/main.go": f'''package main

import (
    "fmt"
    "github.com/extendedsynaptic/xynpos/{service_name}/config"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/delivery/http"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/repository/postgres"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/usecase"
    "github.com/extendedsynaptic/xynpos/shared/pkg/database"
    "github.com/extendedsynaptic/xynpos/shared/pkg/logger"
    "github.com/extendedsynaptic/xynpos/shared/pkg/validator"
    "github.com/gofiber/fiber/v2"
    "go.uber.org/zap"
)

func main() {{
    cfg := config.Load()
    log := logger.New(cfg.LogLevel)
    db  := database.NewPostgres(cfg.DatabaseURL)
    
    // Wire dependencies
    repo    := postgres.New{pascal}Repository(db)
    uc      := usecase.New{pascal}Usecase(repo, log)
    handler := http.New{pascal}Handler(uc, validator.New())
    
    app := fiber.New(fiber.Config{{
        ErrorHandler: http.GlobalErrorHandler,
    }})
    
    http.Register{pascal}Routes(app, handler, cfg.JWTSecret)
    
    log.Info("starting {service_name}", zap.Int("port", cfg.Port))
    if err := app.Listen(fmt.Sprintf(":%d", cfg.Port)); err != nil {{
        log.Fatal("failed to start", zap.Error(err))
    }}
}}
''',
        f"internal/domain/{entity_name}.go": f'''package domain

import "time"

// {pascal} represents the {entity_name} business entity.
type {pascal} struct {{
    ID        string
    TenantID  string
    // TODO: add fields
    IsActive  bool
    CreatedAt time.Time
    UpdatedAt time.Time
    DeletedAt *time.Time
}}
''',
        "internal/domain/errors.go": f'''package domain

import "errors"

var (
    Err{pascal}NotFound    = errors.New("{entity_name} not found")
    Err{pascal}AlreadyExists = errors.New("{entity_name} already exists")
    // TODO: add domain-specific errors
)
''',
        f"internal/repository/{entity_name}_repository.go": f'''package repository

import (
    "context"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/domain"
)

// {pascal}Repository defines data access for {entity_name}.
type {pascal}Repository interface {{
    FindByID(ctx context.Context, id string) (*domain.{pascal}, error)
    FindAll(ctx context.Context, filter {pascal}Filter) ([]domain.{pascal}, int64, error)
    Create(ctx context.Context, e *domain.{pascal}) error
    Update(ctx context.Context, e *domain.{pascal}) error
    SoftDelete(ctx context.Context, id string) error
}}

type {pascal}Filter struct {{
    Search  string
    Page    int
    PerPage int
}}
''',
        f"internal/repository/postgres/{entity_name}_postgres.go": f'''package postgres

import (
    "context"
    "fmt"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/domain"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/repository"
    "gorm.io/gorm"
)

type {camel}Repo struct {{
    db *gorm.DB
}}

func New{pascal}Repository(db *gorm.DB) repository.{pascal}Repository {{
    return &{camel}Repo{{db: db}}
}}

func (r *{camel}Repo) FindByID(ctx context.Context, id string) (*domain.{pascal}, error) {{
    var e domain.{pascal}
    result := r.db.WithContext(ctx).
        Select("id", "tenant_id", "is_active", "created_at", "updated_at").
        Where("id = ? AND deleted_at IS NULL", id).
        First(&e)
    if result.Error != nil {{
        if result.Error == gorm.ErrRecordNotFound {{
            return nil, domain.Err{pascal}NotFound
        }}
        return nil, fmt.Errorf("find {entity_name} by id: %w", result.Error)
    }}
    return &e, nil
}}

func (r *{camel}Repo) FindAll(ctx context.Context, filter repository.{pascal}Filter) ([]domain.{pascal}, int64, error) {{
    var items []domain.{pascal}
    var total int64
    
    q := r.db.WithContext(ctx).Model(&domain.{pascal}{{}}).Where("deleted_at IS NULL")
    
    if filter.Search != "" {{
        // TODO: add search condition
    }}
    
    q.Count(&total)
    if err := q.Limit(filter.PerPage).Offset((filter.Page-1)*filter.PerPage).Find(&items).Error; err != nil {{
        return nil, 0, fmt.Errorf("find all {entity_name}: %w", err)
    }}
    return items, total, nil
}}

func (r *{camel}Repo) Create(ctx context.Context, e *domain.{pascal}) error {{
    if err := r.db.WithContext(ctx).Create(e).Error; err != nil {{
        return fmt.Errorf("create {entity_name}: %w", err)
    }}
    return nil
}}

func (r *{camel}Repo) Update(ctx context.Context, e *domain.{pascal}) error {{
    if err := r.db.WithContext(ctx).Save(e).Error; err != nil {{
        return fmt.Errorf("update {entity_name}: %w", err)
    }}
    return nil
}}

func (r *{camel}Repo) SoftDelete(ctx context.Context, id string) error {{
    if err := r.db.WithContext(ctx).Model(&domain.{pascal}{{}}).
        Where("id = ?", id).Update("deleted_at", "NOW()").Error; err != nil {{
        return fmt.Errorf("soft delete {entity_name}: %w", err)
    }}
    return nil
}}
''',
        f"internal/usecase/{entity_name}_usecase.go": f'''package usecase

import (
    "context"
    "github.com/extendedsynaptic/xynpos/{service_name}/internal/domain"
)

type {pascal}Usecase interface {{
    Get{pascal}(ctx context.Context, tenantID, id string) (*domain.{pascal}, error)
    List{pascal}s(ctx context.Context, tenantID string, req List{pascal}Request) ([]domain.{pascal}, int64, error)
    Create{pascal}(ctx context.Context, tenantID string, req Create{pascal}Request) (*domain.{pascal}, error)
    Update{pascal}(ctx context.Context, tenantID, id string, req Update{pascal}Request) (*domain.{pascal}, error)
    Delete{pascal}(ctx context.Context, tenantID, id string) error
}}
''',
        "config/config.go": f'''package config

import (
    "github.com/spf13/viper"
    "log"
)

type Config struct {{
    Port        int    `mapstructure:"APP_PORT"`
    LogLevel    string `mapstructure:"APP_LOG_LEVEL"`
    DatabaseURL string `mapstructure:"DATABASE_URL"`
    RedisURL    string `mapstructure:"REDIS_URL"`
    JWTSecret   string `mapstructure:"JWT_ACCESS_SECRET"`
}}

func Load() *Config {{
    viper.SetConfigFile(".env.local")
    viper.AutomaticEnv()
    _ = viper.ReadInConfig()
    
    cfg := &Config{{}}
    if err := viper.Unmarshal(cfg); err != nil {{
        log.Fatalf("failed to load config: %v", err)
    }}
    
    // Defaults
    if cfg.Port == 0 {{ cfg.Port = 8000 }}
    if cfg.LogLevel == "" {{ cfg.LogLevel = "info" }}
    
    return cfg
}}
''',
        ".env.example": f'''APP_PORT=8000
APP_LOG_LEVEL=debug
APP_ENV=development

DATABASE_URL=postgres://xynpos:devpassword@localhost:5432/xynpos?sslmode=disable
REDIS_URL=redis://:devredispassword@localhost:6379/0

JWT_ACCESS_SECRET=change_me_in_production_min_32_chars
''',
        "Makefile": f'''# {service_name} Makefile

.PHONY: run test lint swagger mock migrate-up

run:
\tgo run ./cmd/main.go

test:
\tgo test ./... -v -coverprofile=coverage.out
\tgo tool cover -func=coverage.out | grep total

lint:
\tgolangci-lint run ./...

swagger:
\tswag init -g cmd/main.go -o docs/

mock:
\tmockery --all --dir internal/repository --output internal/repository/mock

migrate-up:
\tmigrate -path ./migrations -database "${{DATABASE_URL}}" up

migrate-down:
\tmigrate -path ./migrations -database "${{DATABASE_URL}}" down 1

check-rules:
\tpython scripts/check_rules.py ./internal/
''',
        "go.mod": f'''module github.com/extendedsynaptic/xynpos/{service_name}

go 1.22

require (
    github.com/extendedsynaptic/xynpos/shared v0.0.0
    github.com/gofiber/fiber/v2 v2.52.0
    github.com/golang-jwt/jwt/v5 v5.2.1
    github.com/google/uuid v1.6.0
    github.com/spf13/viper v1.18.2
    github.com/stretchr/testify v1.9.0
    go.uber.org/zap v1.27.0
    gorm.io/driver/postgres v1.5.7
    gorm.io/gorm v1.25.8
)

replace github.com/extendedsynaptic/xynpos/shared => ../../shared
''',
    }
    
    print(f"\n📦 Scaffolding {service_name} with entity: {pascal}")
    print(f"📁 Output: {base}\n")
    
    for rel_path, content in files.items():
        full_path = base / rel_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
        print(f"  ✅ Created: {rel_path}")
    
    # Create empty dirs
    for empty_dir in ["migrations", "internal/repository/mock", "internal/usecase", "internal/delivery/http"]:
        (base / empty_dir).mkdir(parents=True, exist_ok=True)
    
    print(f"\n✨ Done! Service scaffolded at: {base}")
    print(f"\nNext steps:")
    print(f"  1. Add your domain fields to internal/domain/{entity_name}.go")
    print(f"  2. Implement usecase in internal/usecase/{entity_name}_usecase_impl.go")
    print(f"  3. Add HTTP handler in internal/delivery/http/{entity_name}_handler.go")
    print(f"  4. Create migration in migrations/")
    print(f"  5. Run: make run")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <service-name> <entity-name> [output-dir]")
        print("\nExample:")
        print(f"  python {sys.argv[0]} promotion-service promotion")
        print(f"  python {sys.argv[0]} kds-service order /tmp/output")
        sys.exit(1)
    
    service = sys.argv[1]
    entity = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) > 3 else "."
    
    scaffold(service, entity, output)
