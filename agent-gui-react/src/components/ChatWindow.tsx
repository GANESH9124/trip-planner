import React, { useState } from 'react';
import { planVacation, researchPlan, generateDraft, critiqueDraft } from '../services/agentService';

interface Message {
    sender: 'User' | 'Agent';
    content: string;
}

const ChatWindow: React.FC = () => {
    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);

    const displayMessage = (content: string, sender: 'Agent' | 'User' = 'Agent') => {
        const newMessage: Message = { sender, content };
        setMessages((prevMessages) => [...prevMessages, newMessage]);
    };

    const handleSendMessage = async () => {
        if (!input.trim()) return;

        const userMessage: Message = { sender: 'User', content: input };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        const currentInput = input;
        setInput('');
        setLoading(true);

        try {
            // Step 1: Plan
            displayMessage('Planning your vacation...');
            const planResult = await planVacation(currentInput);
            const threadId = planResult.thread_id;
            const plan = planResult.plan || '';
            displayMessage(`📋 Plan: ${plan || 'Plan generated'}`);
            
            // Step 2: Research Plan
            displayMessage('Researching plan...');
            const researchResult = await researchPlan(plan, threadId);
            const queries = researchResult.queries || [];
            const answers = researchResult.answers || [];
            displayMessage(`🔍 Research Queries: ${queries.length > 0 ? queries.join(', ') : 'No queries'}`);
            displayMessage(`📚 Answers: ${answers.length > 0 ? answers.join(', ') : 'No answers'}`);
            
            // Step 3: Generate Draft
            displayMessage('Generating draft...');
            const draftResult = await generateDraft(currentInput, plan, threadId);
            const draft = draftResult.draft || '';
            displayMessage(`✍️ Draft: ${draft || 'Draft generated'}`);
            
            // Step 4: Critique
            displayMessage('Critiquing draft...');
            const critiqueResult = await critiqueDraft(draft, threadId);
            displayMessage(`💭 Critique: ${critiqueResult.critique || 'Critique generated'}`);
            displayMessage(`✅ Process completed!`);
                
        } catch (error: unknown) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred';
            displayMessage(`❌ Error: ${errorMessage}`, 'Agent');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="chat-window">
            <div className="messages">
                {messages.map((msg, index) => (
                    <div key={index} className={`message ${msg.sender.toLowerCase()}`}>
                        <strong>{msg.sender}:</strong> {msg.content}
                    </div>
                ))}
            </div>
            <div className="input-area">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !loading && handleSendMessage()}
                    placeholder="Type your vacation request..."
                    disabled={loading}
                />
                <button onClick={handleSendMessage} disabled={loading}>
                    {loading ? 'Processing...' : 'Send'}
                </button>
            </div>
        </div>
    );
};

export default ChatWindow;