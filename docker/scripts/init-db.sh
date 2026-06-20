#!/bin/bash
# 数据库初始化脚本

set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- 创建扩展
    CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
    
    -- 创建表（如果不存在）
    CREATE TABLE IF NOT EXISTS users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        username VARCHAR(255) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        avatar_url VARCHAR(512),
        preferences JSONB DEFAULT '{}',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
    
    -- 视频表
    CREATE TABLE IF NOT EXISTS videos (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id),
        title VARCHAR(512) NOT NULL,
        game_type VARCHAR(64),
        file_path VARCHAR(1024),
        file_size BIGINT,
        status VARCHAR(32) NOT NULL DEFAULT 'uploading',
        duration_seconds INTEGER,
        thumbnail_path VARCHAR(1024),
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_videos_user_id ON videos(user_id);
    CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
    CREATE INDEX IF NOT EXISTS idx_videos_game_type ON videos(game_type);
    
    -- 视频帧表
    CREATE TABLE IF NOT EXISTS video_frames (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        video_id UUID NOT NULL REFERENCES videos(id),
        frame_number INTEGER NOT NULL,
        timestamp VARCHAR(32) NOT NULL,
        frame_path VARCHAR(1024) NOT NULL,
        is_keyframe INTEGER DEFAULT 0,
        keyframe_score VARCHAR(32)
    );
    
    CREATE INDEX IF NOT EXISTS idx_video_frames_video_id ON video_frames(video_id);
    
    -- 音频转录表
    CREATE TABLE IF NOT EXISTS audio_transcripts (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        video_id UUID NOT NULL REFERENCES videos(id),
        start_time VARCHAR(32) NOT NULL,
        end_time VARCHAR(32) NOT NULL,
        transcript TEXT NOT NULL,
        speaker_info VARCHAR,
        confidence VARCHAR(16)
    );
    
    CREATE INDEX IF NOT EXISTS idx_audio_transcripts_video_id ON audio_transcripts(video_id);
    
    -- 游戏事件表
    CREATE TABLE IF NOT EXISTS game_events (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        video_id UUID NOT NULL REFERENCES videos(id),
        event_id VARCHAR(64) NOT NULL,
        timestamp VARCHAR(32) NOT NULL,
        event_type VARCHAR(64) NOT NULL,
        description TEXT NOT NULL,
        confidence VARCHAR(16),
        metadata VARCHAR
    );
    
    CREATE INDEX IF NOT EXISTS idx_game_events_video_id ON game_events(video_id);
    CREATE INDEX IF NOT EXISTS idx_game_events_type ON game_events(event_type);
    
    -- 报告表
    CREATE TABLE IF NOT EXISTS reports (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        video_id UUID UNIQUE NOT NULL REFERENCES videos(id),
        user_id UUID NOT NULL REFERENCES users(id),
        title VARCHAR(512) NOT NULL,
        markdown_content TEXT NOT NULL,
        summary TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_reports_video_id ON reports(video_id);
    CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
    
    -- 评分表
    CREATE TABLE IF NOT EXISTS scores (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        report_id UUID UNIQUE NOT NULL REFERENCES reports(id),
        operation_score INTEGER NOT NULL,
        awareness_score INTEGER NOT NULL,
        decision_score INTEGER NOT NULL,
        teamwork_score INTEGER NOT NULL,
        replay_score INTEGER NOT NULL,
        score_details JSONB DEFAULT '{}',
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_scores_report_id ON scores(report_id);
    
    -- 建议表
    CREATE TABLE IF NOT EXISTS recommendations (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        report_id UUID NOT NULL REFERENCES reports(id),
        category VARCHAR(128) NOT NULL,
        content TEXT NOT NULL,
        priority INTEGER DEFAULT 1,
        is_actionable INTEGER DEFAULT 1,
        created_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_recommendations_report_id ON recommendations(report_id);
    
    -- 成长记录表
    CREATE TABLE IF NOT EXISTS growth_records (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID NOT NULL REFERENCES users(id),
        record_date DATE NOT NULL,
        total_replays INTEGER DEFAULT 0,
        avg_replay_score FLOAT,
        ability_radar JSONB DEFAULT '{}',
        trend_data JSONB DEFAULT '{}',
        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP NOT NULL DEFAULT NOW()
    );
    
    CREATE INDEX IF NOT EXISTS idx_growth_records_user_id ON growth_records(user_id);
    CREATE INDEX IF NOT EXISTS idx_growth_records_date ON growth_records(record_date);
    
EOSQL

echo "Database initialized successfully"
