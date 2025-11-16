export interface AgentState {
    task: string;
    plan: string;
    answers: string[];
    queries: string[];
    draft: string;
    critique: string;
    revision_number: number;
    max_revisions: number;
}

export interface QueryResult {
    content: string;
}

export interface ResearchResponse {
    results: QueryResult[];
}

export interface PlanResponse {
    plan: string;
}

export interface CritiqueResponse {
    critique: string;
}