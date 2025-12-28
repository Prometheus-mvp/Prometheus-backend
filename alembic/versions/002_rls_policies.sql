-- RLS Policies for Prometheus v1 Backend
-- Run this SQL file in Supabase SQL Editor after running the initial migration
-- All policies use auth.uid() for user isolation

-- Enable RLS on all user-owned tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE linked_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE oauth_tokens ENABLE ROW LEVEL SECURITY;
ALTER TABLE threads ENABLE ROW LEVEL SECURITY;
ALTER TABLE events ENABLE ROW LEVEL SECURITY;
ALTER TABLE entities ENABLE ROW LEVEL SECURITY;
ALTER TABLE notes ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE calendar_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE summaries ENABLE ROW LEVEL SECURITY;
ALTER TABLE proposals ENABLE ROW LEVEL SECURITY;
ALTER TABLE drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE embeddings ENABLE ROW LEVEL SECURITY;

-- Users: Users can only read/update their own record
CREATE POLICY "Users can view own user record"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own user record"
    ON users FOR UPDATE
    USING (auth.uid() = id);

-- Linked accounts: Users can only access their own accounts
CREATE POLICY "Users can view own linked accounts"
    ON linked_accounts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own linked accounts"
    ON linked_accounts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own linked accounts"
    ON linked_accounts FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own linked accounts"
    ON linked_accounts FOR DELETE
    USING (auth.uid() = user_id);

-- OAuth tokens: Users can only access tokens for their accounts
CREATE POLICY "Users can view own oauth tokens"
    ON oauth_tokens FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own oauth tokens"
    ON oauth_tokens FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own oauth tokens"
    ON oauth_tokens FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own oauth tokens"
    ON oauth_tokens FOR DELETE
    USING (auth.uid() = user_id);

-- Threads: Users can only access their own threads
CREATE POLICY "Users can view own threads"
    ON threads FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own threads"
    ON threads FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own threads"
    ON threads FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own threads"
    ON threads FOR DELETE
    USING (auth.uid() = user_id);

-- Events: Users can only access their own events
CREATE POLICY "Users can view own events"
    ON events FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own events"
    ON events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own events"
    ON events FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own events"
    ON events FOR DELETE
    USING (auth.uid() = user_id);

-- Entities: Users can only access their own entities
CREATE POLICY "Users can view own entities"
    ON entities FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own entities"
    ON entities FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own entities"
    ON entities FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own entities"
    ON entities FOR DELETE
    USING (auth.uid() = user_id);

-- Notes: Users can only access their own notes
CREATE POLICY "Users can view own notes"
    ON notes FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own notes"
    ON notes FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own notes"
    ON notes FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own notes"
    ON notes FOR DELETE
    USING (auth.uid() = user_id);

-- Tasks: Users can only access their own tasks
CREATE POLICY "Users can view own tasks"
    ON tasks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own tasks"
    ON tasks FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own tasks"
    ON tasks FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own tasks"
    ON tasks FOR DELETE
    USING (auth.uid() = user_id);

-- Calendar events: Users can only access their own calendar events
CREATE POLICY "Users can view own calendar events"
    ON calendar_events FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own calendar events"
    ON calendar_events FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own calendar events"
    ON calendar_events FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own calendar events"
    ON calendar_events FOR DELETE
    USING (auth.uid() = user_id);

-- Summaries: Users can only access their own summaries
CREATE POLICY "Users can view own summaries"
    ON summaries FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own summaries"
    ON summaries FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own summaries"
    ON summaries FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own summaries"
    ON summaries FOR DELETE
    USING (auth.uid() = user_id);

-- Proposals: Users can only access their own proposals
CREATE POLICY "Users can view own proposals"
    ON proposals FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own proposals"
    ON proposals FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own proposals"
    ON proposals FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own proposals"
    ON proposals FOR DELETE
    USING (auth.uid() = user_id);

-- Drafts: Users can only access their own drafts
CREATE POLICY "Users can view own drafts"
    ON drafts FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own drafts"
    ON drafts FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own drafts"
    ON drafts FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own drafts"
    ON drafts FOR DELETE
    USING (auth.uid() = user_id);

-- Embeddings: Users can only access their own embeddings
CREATE POLICY "Users can view own embeddings"
    ON embeddings FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own embeddings"
    ON embeddings FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own embeddings"
    ON embeddings FOR UPDATE
    USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own embeddings"
    ON embeddings FOR DELETE
    USING (auth.uid() = user_id);

