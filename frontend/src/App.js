import React, { useState, useEffect, useRef, useCallback } from "react";
import "@/App.css";
import axios from "axios";
import { Toaster, toast } from "sonner";
import { 
  MessageSquare, 
  Plus, 
  Settings, 
  Webhook, 
  Bot, 
  Trash2, 
  Send, 
  Loader2,
  ChevronDown,
  Zap,
  Brain,
  Activity,
  AlertCircle,
  Check,
  Play,
  Pause,
  MoreVertical,
  Link2,
  Copy,
  TrendingUp,
  TrendingDown,
  Wallet,
  DollarSign,
  RefreshCw,
  Eye,
  EyeOff,
  Unlink
} from "lucide-react";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// ============= CRYPTO TICKER COMPONENT =============
const CryptoTicker = ({ prices, loading }) => {
  if (loading) {
    return (
      <div className="bg-surface border-b border-border px-4 py-2">
        <div className="flex items-center gap-2 text-muted-foreground text-sm">
          <RefreshCw className="w-3 h-3 animate-spin" />
          Loading prices...
        </div>
      </div>
    );
  }

  if (!prices || prices.length === 0) return null;

  return (
    <div className="bg-surface border-b border-border overflow-hidden" data-testid="crypto-ticker">
      <div className="flex animate-scroll">
        {[...prices, ...prices].map((coin, idx) => (
          <div 
            key={`${coin.symbol}-${idx}`}
            className="flex items-center gap-3 px-4 py-2 border-r border-border min-w-fit"
          >
            <img src={coin.image} alt={coin.symbol} className="w-5 h-5 rounded-full" />
            <span className="font-mono font-medium text-sm">{coin.symbol}</span>
            <span className="font-mono text-sm">${coin.price?.toLocaleString(undefined, { maximumFractionDigits: 2 })}</span>
            <span className={`flex items-center text-xs font-mono ${coin.change_24h >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {coin.change_24h >= 0 ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
              {coin.change_24h?.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  )
};

// ============= SIDEBAR COMPONENT =============
const Sidebar = ({ 
  conversations, 
  activeConversation, 
  onSelectConversation, 
  onNewChat, 
  onDeleteConversation,
  activeTab,
  onTabChange
}) => {
  return (
    <div className="w-64 bg-surface border-r border-border flex flex-col h-full" data-testid="sidebar">
      {/* Logo */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-sm bg-primary flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <span className="font-heading font-semibold text-lg">E1 Assistant</span>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="p-2 border-b border-border">
        <nav className="flex flex-col gap-1">
          <button
            data-testid="nav-chat"
            onClick={() => onTabChange('chat')}
            className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors ${
              activeTab === 'chat' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-surface-highlight'
            }`}
          >
            <MessageSquare className="w-4 h-4" />
            Chat
          </button>
          <button
            data-testid="nav-integrations"
            onClick={() => onTabChange('integrations')}
            className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors ${
              activeTab === 'integrations' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-surface-highlight'
            }`}
          >
            <Webhook className="w-4 h-4" />
            Integrations
          </button>
          <button
            data-testid="nav-swarm"
            onClick={() => onTabChange('swarm')}
            className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors ${
              activeTab === 'swarm' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-surface-highlight'
            }`}
          >
            <Bot className="w-4 h-4" />
            Swarm Agents
          </button>
          <button
            data-testid="nav-settings"
            onClick={() => onTabChange('settings')}
            className={`flex items-center gap-2 px-3 py-2 rounded-sm text-sm transition-colors ${
              activeTab === 'settings' ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:bg-surface-highlight'
            }`}
          >
            <Settings className="w-4 h-4" />
            Settings
          </button>
        </nav>
      </div>

      {/* Conversation List (only show in chat tab) */}
      {activeTab === 'chat' && (
        <>
          <div className="p-2">
            <button
              data-testid="new-chat-btn"
              onClick={onNewChat}
              className="w-full flex items-center gap-2 px-3 py-2 rounded-sm bg-primary text-white text-sm font-medium hover:bg-primary/90 transition-colors"
            >
              <Plus className="w-4 h-4" />
              New Chat
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2">
            <div className="text-xs uppercase tracking-widest text-muted-foreground px-3 py-2 font-mono">
              Recent Chats
            </div>
            {conversations.map((conv) => (
              <div
                key={conv.id}
                data-testid={`conversation-${conv.id}`}
                className={`group flex items-center gap-2 px-3 py-2 rounded-sm cursor-pointer transition-colors ${
                  activeConversation?.id === conv.id
                    ? 'bg-primary/10 text-primary'
                    : 'text-muted-foreground hover:bg-surface-highlight'
                }`}
                onClick={() => onSelectConversation(conv)}
              >
                <MessageSquare className="w-4 h-4 flex-shrink-0" />
                <span className="flex-1 truncate text-sm">{conv.title}</span>
                <button
                  data-testid={`delete-conversation-${conv.id}`}
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteConversation(conv.id);
                  }}
                  className="opacity-0 group-hover:opacity-100 p-1 hover:text-destructive transition-opacity"
                >
                  <Trash2 className="w-3 h-3" />
                </button>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
};

// ============= MODEL SELECTOR COMPONENT =============
const ModelSelector = ({ models, selectedModel, onSelectModel }) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const currentModel = models.find(m => m.model === selectedModel.model) || models[0];

  return (
    <div className="relative">
      <button
        data-testid="model-selector"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-1.5 rounded-sm bg-surface-highlight border border-border text-sm hover:border-primary/50 transition-colors"
      >
        <Brain className="w-4 h-4 text-primary" />
        <span>{currentModel?.name}</span>
        <ChevronDown className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-surface border border-border rounded-sm shadow-lg z-50 animate-fade-in">
          {models.map((model) => (
            <button
              key={`${model.provider}-${model.model}`}
              data-testid={`model-option-${model.model}`}
              onClick={() => {
                onSelectModel(model);
                setIsOpen(false);
              }}
              className={`w-full flex items-center gap-3 px-3 py-2 text-left text-sm hover:bg-surface-highlight transition-colors ${
                model.model === selectedModel.model ? 'bg-primary/10 text-primary' : ''
              }`}
            >
              <div className="flex-1">
                <div className="font-medium">{model.name}</div>
                <div className="text-xs text-muted-foreground capitalize">{model.provider}</div>
              </div>
              {model.recommended && (
                <span className="text-xs px-1.5 py-0.5 bg-accent/20 text-accent rounded">
                  Recommended
                </span>
              )}
            </button>
          ))}
        </div>
      )}
    </div>
  );
};

// ============= CHAT MESSAGE COMPONENT =============
const ChatMessage = ({ message, isUser }) => {
  return (
    <div
      data-testid={`message-${message.id}`}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}
    >
      <div
        className={`max-w-[80%] px-4 py-3 ${
          isUser
            ? 'bg-primary text-white message-user'
            : 'bg-surface-highlight text-foreground message-assistant'
        }`}
      >
        <div className="whitespace-pre-wrap break-words">{message.content}</div>
        {message.model && !isUser && (
          <div className="mt-2 text-xs text-muted-foreground font-mono">
            via {message.model}
          </div>
        )}
      </div>
    </div>
  );
};

// ============= CHAT INTERFACE COMPONENT =============
const ChatInterface = ({ 
  conversation, 
  models, 
  selectedModel, 
  onSelectModel, 
  onSendMessage, 
  isLoading 
}) => {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation?.messages]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full" data-testid="chat-interface">
      {/* Header */}
      <div className="p-4 border-b border-border flex items-center justify-between">
        <div>
          <h2 className="font-heading font-semibold">
            {conversation?.title || 'New Chat'}
          </h2>
          <p className="text-sm text-muted-foreground">
            {conversation?.messages?.length || 0} messages
          </p>
        </div>
        <ModelSelector 
          models={models} 
          selectedModel={selectedModel} 
          onSelectModel={onSelectModel} 
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 grid-pattern">
        {(!conversation?.messages || conversation.messages.length === 0) ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
                <Zap className="w-8 h-8 text-primary" />
              </div>
              <h3 className="font-heading font-semibold text-xl mb-2">
                Welcome to E1 Assistant
              </h3>
              <p className="text-muted-foreground max-w-md">
                Start a conversation with AI. Choose your model above and ask anything.
              </p>
            </div>
          </div>
        ) : (
          conversation.messages.map((msg) => (
            <ChatMessage 
              key={msg.id} 
              message={msg} 
              isUser={msg.role === 'user'} 
            />
          ))
        )}
        {isLoading && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-surface-highlight px-4 py-3 rounded-lg rounded-tl-none">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSubmit} className="p-4 pb-16 border-t border-border">
        <div className="flex gap-2">
          <input
            data-testid="chat-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            className="flex-1 bg-surface-highlight border border-border rounded-sm px-4 py-2 text-foreground placeholder:text-muted-foreground focus:outline-none focus:border-primary transition-colors"
            disabled={isLoading}
          />
          <button
            data-testid="send-btn"
            type="submit"
            disabled={!input.trim() || isLoading}
            className="px-4 py-2 bg-primary text-white rounded-sm hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
};

// ============= INTEGRATIONS PAGE COMPONENT =============
const IntegrationsPage = ({ webhooks, onAddWebhook, onDeleteWebhook, onTestWebhook }) => {
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    url: '',
    method: 'POST',
    headers: {}
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onAddWebhook(formData);
    setFormData({ name: '', description: '', url: '', method: 'POST', headers: {} });
    setShowForm(false);
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto" data-testid="integrations-page">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="font-heading font-semibold text-2xl">Integrations</h1>
            <p className="text-muted-foreground">Connect your apps and services via webhooks</p>
          </div>
          <button
            data-testid="add-webhook-btn"
            onClick={() => setShowForm(true)}
            className="flex items-center gap-2 px-4 py-2 bg-primary text-white rounded-sm hover:bg-primary/90 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Webhook
          </button>
        </div>

        {showForm && (
          <div className="bg-surface border border-border rounded-sm p-6 mb-6 animate-fade-in">
            <h3 className="font-heading font-semibold mb-4">New Webhook</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm text-muted-foreground mb-1">Name</label>
                <input
                  data-testid="webhook-name-input"
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-muted-foreground mb-1">URL</label>
                <input
                  data-testid="webhook-url-input"
                  type="url"
                  value={formData.url}
                  onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                  placeholder="https://api.example.com/webhook"
                  className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                  required
                />
              </div>
              <div>
                <label className="block text-sm text-muted-foreground mb-1">Method</label>
                <select
                  data-testid="webhook-method-select"
                  value={formData.method}
                  onChange={(e) => setFormData({ ...formData, method: e.target.value })}
                  className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                >
                  <option value="POST">POST</option>
                  <option value="GET">GET</option>
                  <option value="PUT">PUT</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-muted-foreground mb-1">Description (optional)</label>
                <textarea
                  data-testid="webhook-description-input"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                  rows="2"
                />
              </div>
              <div className="flex gap-2">
                <button
                  data-testid="save-webhook-btn"
                  type="submit"
                  className="px-4 py-2 bg-primary text-white rounded-sm hover:bg-primary/90"
                >
                  Save Webhook
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 bg-secondary text-secondary-foreground rounded-sm hover:bg-secondary/80"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="space-y-4">
          {webhooks.length === 0 ? (
            <div className="text-center py-12 bg-surface border border-border rounded-sm">
              <Link2 className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <h3 className="font-heading font-medium mb-2">No webhooks configured</h3>
              <p className="text-muted-foreground">Add your first webhook to connect external services</p>
            </div>
          ) : (
            webhooks.map((webhook) => (
              <div
                key={webhook.id}
                data-testid={`webhook-${webhook.id}`}
                className="bg-surface border border-border rounded-sm p-4 hover:border-primary/50 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium">{webhook.name}</h3>
                      <span className="text-xs px-2 py-0.5 bg-primary/20 text-primary rounded font-mono">
                        {webhook.method}
                      </span>
                      {webhook.enabled && <span className="status-online" />}
                    </div>
                    <p className="text-sm text-muted-foreground mt-1 font-mono truncate">
                      {webhook.url}
                    </p>
                    {webhook.description && (
                      <p className="text-sm text-muted-foreground mt-2">{webhook.description}</p>
                    )}
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      data-testid={`test-webhook-${webhook.id}`}
                      onClick={() => onTestWebhook(webhook.id)}
                      className="p-2 hover:bg-surface-highlight rounded-sm transition-colors"
                      title="Test webhook"
                    >
                      <Play className="w-4 h-4" />
                    </button>
                    <button
                      data-testid={`delete-webhook-${webhook.id}`}
                      onClick={() => onDeleteWebhook(webhook.id)}
                      className="p-2 hover:bg-surface-highlight rounded-sm text-destructive transition-colors"
                      title="Delete webhook"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

// ============= SWARM AGENTS PAGE COMPONENT =============
const SwarmPage = ({ agents, tasks, onAddAgent, onDeleteAgent, onCreateTask }) => {
  const [showAgentForm, setShowAgentForm] = useState(false);
  const [showTaskForm, setShowTaskForm] = useState(false);
  const [agentForm, setAgentForm] = useState({
    name: '',
    role: 'analyst',
    model: 'gemini-3-flash-preview',
    provider: 'gemini',
    system_prompt: ''
  });
  const [taskForm, setTaskForm] = useState({
    name: '',
    task_type: 'analysis',
    agents: [],
    input_data: ''
  });

  const rolePrompts = {
    analyst: "You are a crypto market analyst. Analyze market data, identify trends, and provide insights on trading opportunities.",
    trader: "You are a crypto trader agent. Based on analysis and signals, suggest specific trades with entry/exit points and position sizes.",
    risk_manager: "You are a risk management specialist. Evaluate positions, calculate risk/reward ratios, and suggest protective measures.",
    coordinator: "You are a swarm coordinator. Synthesize information from other agents and make final trading decisions."
  };

  const handleAgentSubmit = (e) => {
    e.preventDefault();
    onAddAgent({
      ...agentForm,
      system_prompt: agentForm.system_prompt || rolePrompts[agentForm.role]
    });
    setAgentForm({ name: '', role: 'analyst', model: 'gemini-3-flash-preview', provider: 'gemini', system_prompt: '' });
    setShowAgentForm(false);
  };

  const handleTaskSubmit = (e) => {
    e.preventDefault();
    let inputData = {};
    try {
      inputData = JSON.parse(taskForm.input_data || '{}');
    } catch {
      inputData = { raw: taskForm.input_data };
    }
    onCreateTask({
      name: taskForm.name,
      task_type: taskForm.task_type,
      agents: taskForm.agents,
      input_data: inputData
    });
    setTaskForm({ name: '', task_type: 'analysis', agents: [], input_data: '' });
    setShowTaskForm(false);
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto" data-testid="swarm-page">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="font-heading font-semibold text-2xl mb-2">Swarm Agents</h1>
          <p className="text-muted-foreground">
            Multi-agent system for collaborative crypto trading analysis
          </p>
        </div>

        {/* Agents Section */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-medium text-lg">Agents</h2>
            <button
              data-testid="add-agent-btn"
              onClick={() => setShowAgentForm(true)}
              className="flex items-center gap-2 px-3 py-1.5 bg-primary text-white text-sm rounded-sm hover:bg-primary/90"
            >
              <Plus className="w-4 h-4" />
              Add Agent
            </button>
          </div>

          {showAgentForm && (
            <div className="bg-surface border border-border rounded-sm p-6 mb-4 animate-fade-in">
              <h3 className="font-heading font-semibold mb-4">New Agent</h3>
              <form onSubmit={handleAgentSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-muted-foreground mb-1">Name</label>
                    <input
                      data-testid="agent-name-input"
                      type="text"
                      value={agentForm.name}
                      onChange={(e) => setAgentForm({ ...agentForm, name: e.target.value })}
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-muted-foreground mb-1">Role</label>
                    <select
                      data-testid="agent-role-select"
                      value={agentForm.role}
                      onChange={(e) => setAgentForm({ ...agentForm, role: e.target.value })}
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                    >
                      <option value="analyst">Market Analyst</option>
                      <option value="trader">Trader</option>
                      <option value="risk_manager">Risk Manager</option>
                      <option value="coordinator">Coordinator</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-muted-foreground mb-1">Provider</label>
                    <select
                      data-testid="agent-provider-select"
                      value={agentForm.provider}
                      onChange={(e) => setAgentForm({ ...agentForm, provider: e.target.value })}
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                    >
                      <option value="gemini">Gemini</option>
                      <option value="anthropic">Anthropic</option>
                      <option value="openai">OpenAI</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-muted-foreground mb-1">Model</label>
                    <select
                      data-testid="agent-model-select"
                      value={agentForm.model}
                      onChange={(e) => setAgentForm({ ...agentForm, model: e.target.value })}
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                    >
                      <option value="gemini-3-flash-preview">Gemini 3 Flash</option>
                      <option value="claude-sonnet-4-5-20250929">Claude Sonnet 4.5</option>
                      <option value="gpt-5.1">GPT-5.1</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">
                    System Prompt (optional - uses role default if empty)
                  </label>
                  <textarea
                    data-testid="agent-prompt-input"
                    value={agentForm.system_prompt}
                    onChange={(e) => setAgentForm({ ...agentForm, system_prompt: e.target.value })}
                    placeholder={rolePrompts[agentForm.role]}
                    className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                    rows="3"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    data-testid="save-agent-btn"
                    type="submit"
                    className="px-4 py-2 bg-primary text-white rounded-sm hover:bg-primary/90"
                  >
                    Create Agent
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowAgentForm(false)}
                    className="px-4 py-2 bg-secondary text-secondary-foreground rounded-sm hover:bg-secondary/80"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {agents.length === 0 ? (
              <div className="col-span-full text-center py-12 bg-surface border border-border rounded-sm">
                <Bot className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                <h3 className="font-heading font-medium mb-2">No agents configured</h3>
                <p className="text-muted-foreground">Create agents to build your trading swarm</p>
              </div>
            ) : (
              agents.map((agent) => (
                <div
                  key={agent.id}
                  data-testid={`agent-${agent.id}`}
                  className="bg-surface border border-border rounded-sm p-4 hover:border-primary/50 transition-colors"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-8 h-8 rounded-sm bg-primary/10 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium">{agent.name}</h3>
                        <span className="text-xs text-muted-foreground capitalize">{agent.role.replace('_', ' ')}</span>
                      </div>
                    </div>
                    <button
                      data-testid={`delete-agent-${agent.id}`}
                      onClick={() => onDeleteAgent(agent.id)}
                      className="p-1 hover:bg-surface-highlight rounded-sm text-destructive"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="text-xs font-mono text-muted-foreground">
                    {agent.provider} / {agent.model}
                  </div>
                  <div className="mt-2 flex items-center gap-2">
                    <span className={`status-${agent.status === 'running' ? 'online' : 'offline'}`} />
                    <span className="text-xs text-muted-foreground capitalize">{agent.status}</span>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Tasks Section */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-heading font-medium text-lg">Tasks</h2>
            <button
              data-testid="create-task-btn"
              onClick={() => setShowTaskForm(true)}
              disabled={agents.length === 0}
              className="flex items-center gap-2 px-3 py-1.5 bg-accent text-white text-sm rounded-sm hover:bg-accent/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Zap className="w-4 h-4" />
              Run Task
            </button>
          </div>

          {showTaskForm && (
            <div className="bg-surface border border-border rounded-sm p-6 mb-4 animate-fade-in">
              <h3 className="font-heading font-semibold mb-4">New Task</h3>
              <form onSubmit={handleTaskSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-muted-foreground mb-1">Task Name</label>
                    <input
                      data-testid="task-name-input"
                      type="text"
                      value={taskForm.name}
                      onChange={(e) => setTaskForm({ ...taskForm, name: e.target.value })}
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                      required
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-muted-foreground mb-1">Task Type</label>
                    <select
                      data-testid="task-type-select"
                      value={taskForm.task_type}
                      onChange={(e) => setTaskForm({ ...taskForm, task_type: e.target.value })}
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                    >
                      <option value="analysis">Market Analysis</option>
                      <option value="trade_signal">Trade Signal</option>
                      <option value="risk_check">Risk Check</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">Select Agents</label>
                  <div className="flex flex-wrap gap-2">
                    {agents.map((agent) => (
                      <label
                        key={agent.id}
                        className={`flex items-center gap-2 px-3 py-1.5 rounded-sm border cursor-pointer transition-colors ${
                          taskForm.agents.includes(agent.id)
                            ? 'border-primary bg-primary/10 text-primary'
                            : 'border-border hover:border-primary/50'
                        }`}
                      >
                        <input
                          type="checkbox"
                          checked={taskForm.agents.includes(agent.id)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setTaskForm({ ...taskForm, agents: [...taskForm.agents, agent.id] });
                            } else {
                              setTaskForm({ ...taskForm, agents: taskForm.agents.filter(id => id !== agent.id) });
                            }
                          }}
                          className="sr-only"
                        />
                        <span className="text-sm">{agent.name}</span>
                      </label>
                    ))}
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">Input Data (JSON)</label>
                  <textarea
                    data-testid="task-input-data"
                    value={taskForm.input_data}
                    onChange={(e) => setTaskForm({ ...taskForm, input_data: e.target.value })}
                    placeholder='{"symbol": "BTC", "timeframe": "1h", "price": 45000}'
                    className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary font-mono text-sm"
                    rows="3"
                  />
                </div>
                <div className="flex gap-2">
                  <button
                    data-testid="submit-task-btn"
                    type="submit"
                    disabled={taskForm.agents.length === 0}
                    className="px-4 py-2 bg-accent text-white rounded-sm hover:bg-accent/90 disabled:opacity-50"
                  >
                    Run Task
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowTaskForm(false)}
                    className="px-4 py-2 bg-secondary text-secondary-foreground rounded-sm hover:bg-secondary/80"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          )}

          <div className="space-y-4">
            {tasks.length === 0 ? (
              <div className="text-center py-8 bg-surface border border-border rounded-sm">
                <Activity className="w-8 h-8 mx-auto mb-2 text-muted-foreground" />
                <p className="text-muted-foreground">No tasks run yet</p>
              </div>
            ) : (
              tasks.map((task) => (
                <div
                  key={task.id}
                  data-testid={`task-${task.id}`}
                  className="bg-surface border border-border rounded-sm p-4"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <h3 className="font-medium">{task.name}</h3>
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        task.status === 'completed' ? 'bg-green-500/20 text-green-400' :
                        task.status === 'running' ? 'bg-primary/20 text-primary' :
                        task.status === 'failed' ? 'bg-destructive/20 text-destructive-foreground' :
                        'bg-muted text-muted-foreground'
                      }`}>
                        {task.status}
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground font-mono">
                      {task.task_type}
                    </span>
                  </div>
                  {task.results && task.results.length > 0 && (
                    <div className="mt-3 space-y-2">
                      {task.results.map((result, idx) => (
                        <div key={idx} className="bg-surface-highlight rounded-sm p-3">
                          <div className="text-xs text-muted-foreground mb-1">
                            {result.agent_name} ({result.agent_role})
                          </div>
                          <div className="text-sm whitespace-pre-wrap">
                            {result.response || result.error}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// ============= SETTINGS PAGE COMPONENT =============
const SettingsPage = ({ settings, models, walletSettings, onUpdateSettings, onUpdateWalletSettings, onDisconnectWallet }) => {
  const [formData, setFormData] = useState(settings);
  const [walletForm, setWalletForm] = useState({
    binance_api_key: '',
    binance_api_secret: '',
    coinbase_api_key: '',
    coinbase_private_key: ''
  });
  const [showBinanceKey, setShowBinanceKey] = useState(false);
  const [showCoinbaseKey, setShowCoinbaseKey] = useState(false);
  const [savingWallet, setSavingWallet] = useState(false);

  useEffect(() => {
    setFormData(settings);
  }, [settings]);

  const handleSave = () => {
    onUpdateSettings(formData);
  };

  const handleSaveWallet = async (exchange) => {
    setSavingWallet(true);
    try {
      if (exchange === 'binance') {
        await onUpdateWalletSettings({
          binance_api_key: walletForm.binance_api_key,
          binance_api_secret: walletForm.binance_api_secret
        });
        setWalletForm(prev => ({ ...prev, binance_api_key: '', binance_api_secret: '' }));
      } else {
        await onUpdateWalletSettings({
          coinbase_api_key: walletForm.coinbase_api_key,
          coinbase_private_key: walletForm.coinbase_private_key
        });
        setWalletForm(prev => ({ ...prev, coinbase_api_key: '', coinbase_private_key: '' }));
      }
    } finally {
      setSavingWallet(false);
    }
  };

  return (
    <div className="flex-1 p-6 overflow-y-auto" data-testid="settings-page">
      <div className="max-w-2xl mx-auto space-y-8">
        <h1 className="font-heading font-semibold text-2xl">Settings</h1>

        {/* Wallet Connections */}
        <div className="bg-surface border border-border rounded-sm p-6">
          <div className="flex items-center gap-2 mb-6">
            <Wallet className="w-5 h-5 text-primary" />
            <h3 className="font-heading font-medium text-lg">Exchange Wallets</h3>
          </div>

          {/* Binance */}
          <div className="mb-6 pb-6 border-b border-border">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-sm bg-yellow-500/10 flex items-center justify-center">
                  <span className="font-bold text-yellow-500">B</span>
                </div>
                <div>
                  <h4 className="font-medium">Binance</h4>
                  <p className="text-xs text-muted-foreground">
                    {walletSettings?.binance_connected 
                      ? `Connected: ${walletSettings.binance_api_key_preview}` 
                      : 'Not connected'}
                  </p>
                </div>
              </div>
              {walletSettings?.binance_connected && (
                <button
                  data-testid="disconnect-binance-btn"
                  onClick={() => onDisconnectWallet('binance')}
                  className="flex items-center gap-1 text-sm text-destructive hover:underline"
                >
                  <Unlink className="w-3 h-3" /> Disconnect
                </button>
              )}
            </div>
            
            {!walletSettings?.binance_connected && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">API Key</label>
                  <div className="relative">
                    <input
                      data-testid="binance-api-key-input"
                      type={showBinanceKey ? "text" : "password"}
                      value={walletForm.binance_api_key}
                      onChange={(e) => setWalletForm({ ...walletForm, binance_api_key: e.target.value })}
                      placeholder="Enter Binance API Key"
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 pr-10 focus:outline-none focus:border-primary"
                    />
                    <button
                      type="button"
                      onClick={() => setShowBinanceKey(!showBinanceKey)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                    >
                      {showBinanceKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">API Secret</label>
                  <input
                    data-testid="binance-api-secret-input"
                    type="password"
                    value={walletForm.binance_api_secret}
                    onChange={(e) => setWalletForm({ ...walletForm, binance_api_secret: e.target.value })}
                    placeholder="Enter Binance API Secret"
                    className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
                  />
                </div>
                <button
                  data-testid="save-binance-btn"
                  onClick={() => handleSaveWallet('binance')}
                  disabled={!walletForm.binance_api_key || !walletForm.binance_api_secret || savingWallet}
                  className="px-4 py-2 bg-yellow-500 text-black rounded-sm hover:bg-yellow-400 disabled:opacity-50 text-sm font-medium"
                >
                  {savingWallet ? 'Connecting...' : 'Connect Binance'}
                </button>
              </div>
            )}
          </div>

          {/* Coinbase */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-sm bg-blue-500/10 flex items-center justify-center">
                  <span className="font-bold text-blue-500">C</span>
                </div>
                <div>
                  <h4 className="font-medium">Coinbase</h4>
                  <p className="text-xs text-muted-foreground">
                    {walletSettings?.coinbase_connected 
                      ? `Connected: ${walletSettings.coinbase_api_key_preview}` 
                      : 'Not connected'}
                  </p>
                </div>
              </div>
              {walletSettings?.coinbase_connected && (
                <button
                  data-testid="disconnect-coinbase-btn"
                  onClick={() => onDisconnectWallet('coinbase')}
                  className="flex items-center gap-1 text-sm text-destructive hover:underline"
                >
                  <Unlink className="w-3 h-3" /> Disconnect
                </button>
              )}
            </div>
            
            {!walletSettings?.coinbase_connected && (
              <div className="space-y-3">
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">API Key</label>
                  <div className="relative">
                    <input
                      data-testid="coinbase-api-key-input"
                      type={showCoinbaseKey ? "text" : "password"}
                      value={walletForm.coinbase_api_key}
                      onChange={(e) => setWalletForm({ ...walletForm, coinbase_api_key: e.target.value })}
                      placeholder="organizations/org-id/apiKeys/key-id"
                      className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 pr-10 focus:outline-none focus:border-primary"
                    />
                    <button
                      type="button"
                      onClick={() => setShowCoinbaseKey(!showCoinbaseKey)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground"
                    >
                      {showCoinbaseKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                    </button>
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-muted-foreground mb-1">Private Key</label>
                  <textarea
                    data-testid="coinbase-private-key-input"
                    value={walletForm.coinbase_private_key}
                    onChange={(e) => setWalletForm({ ...walletForm, coinbase_private_key: e.target.value })}
                    placeholder="-----BEGIN EC PRIVATE KEY-----..."
                    className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary font-mono text-xs"
                    rows="3"
                  />
                </div>
                <button
                  data-testid="save-coinbase-btn"
                  onClick={() => handleSaveWallet('coinbase')}
                  disabled={!walletForm.coinbase_api_key || !walletForm.coinbase_private_key || savingWallet}
                  className="px-4 py-2 bg-blue-500 text-white rounded-sm hover:bg-blue-400 disabled:opacity-50 text-sm font-medium"
                >
                  {savingWallet ? 'Connecting...' : 'Connect Coinbase'}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Model Settings */}
        <div className="bg-surface border border-border rounded-sm p-6 space-y-6">
          <h3 className="font-heading font-medium">Default Model</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-muted-foreground mb-1">Provider</label>
              <select
                data-testid="settings-provider-select"
                value={formData.default_provider || 'anthropic'}
                onChange={(e) => setFormData({ ...formData, default_provider: e.target.value })}
                className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
              >
                <option value="anthropic">Anthropic</option>
                <option value="gemini">Gemini</option>
                <option value="openai">OpenAI</option>
                <option value="moonshot">Moonshot (Kimi)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-muted-foreground mb-1">Model</label>
              <select
                data-testid="settings-model-select"
                value={formData.default_model || 'claude-sonnet-4-5-20250929'}
                onChange={(e) => setFormData({ ...formData, default_model: e.target.value })}
                className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
              >
                {models.map(m => (
                  <option key={m.model} value={m.model}>{m.name}</option>
                ))}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm text-muted-foreground mb-1">System Prompt</label>
            <textarea
              data-testid="settings-system-prompt"
              value={formData.system_prompt || ''}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              placeholder="You are E1, a powerful AI assistant..."
              className="w-full bg-surface-highlight border border-border rounded-sm px-3 py-2 focus:outline-none focus:border-primary"
              rows="4"
            />
          </div>

          <button
            data-testid="save-settings-btn"
            onClick={handleSave}
            className="px-4 py-2 bg-primary text-white rounded-sm hover:bg-primary/90"
          >
            Save Settings
          </button>
        </div>

        {/* About */}
        <div className="bg-surface border border-border rounded-sm p-6">
          <h3 className="font-medium mb-4">About</h3>
          <div className="text-sm text-muted-foreground space-y-2">
            <p><strong>E1 Assistant</strong> - Personal AI Assistant</p>
            <p>Multi-model support with persistent memory, app integrations, swarm agents, and crypto trading capabilities.</p>
            <p className="font-mono text-xs">Powered by Emergent LLM Key • Kimi K2.5 Agent Swarm Ready</p>
          </div>
        </div>
      </div>
    </div>
  );
};

// ============= MAIN APP COMPONENT =============
function App() {
  const [activeTab, setActiveTab] = useState('chat');
  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState({ provider: 'anthropic', model: 'claude-sonnet-4-5-20250929' });
  const [webhooks, setWebhooks] = useState([]);
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [settings, setSettings] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  // Fetch initial data
  useEffect(() => {
    fetchModels();
    fetchConversations();
    fetchWebhooks();
    fetchAgents();
    fetchTasks();
    fetchSettings();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API}/models`);
      setModels(response.data.models);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const fetchWebhooks = async () => {
    try {
      const response = await axios.get(`${API}/webhooks`);
      setWebhooks(response.data);
    } catch (error) {
      console.error('Error fetching webhooks:', error);
    }
  };

  const fetchAgents = async () => {
    try {
      const response = await axios.get(`${API}/swarm/agents`);
      setAgents(response.data);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API}/swarm/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error('Error fetching tasks:', error);
    }
  };

  const fetchSettings = async () => {
    try {
      const response = await axios.get(`${API}/settings`);
      setSettings(response.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleNewChat = () => {
    setActiveConversation(null);
  };

  const handleSelectConversation = async (conv) => {
    try {
      const response = await axios.get(`${API}/conversations/${conv.id}`);
      setActiveConversation(response.data);
    } catch (error) {
      toast.error('Failed to load conversation');
    }
  };

  const handleDeleteConversation = async (id) => {
    try {
      await axios.delete(`${API}/conversations/${id}`);
      setConversations(conversations.filter(c => c.id !== id));
      if (activeConversation?.id === id) {
        setActiveConversation(null);
      }
      toast.success('Conversation deleted');
    } catch (error) {
      toast.error('Failed to delete conversation');
    }
  };

  const handleSendMessage = async (message) => {
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/chat`, {
        conversation_id: activeConversation?.id,
        message,
        model: selectedModel.model,
        provider: selectedModel.provider
      });

      const { conversation_id, message: assistantMsg, title } = response.data;

      // Update or create conversation
      if (!activeConversation) {
        const newConv = {
          id: conversation_id,
          title,
          messages: [
            { id: Date.now().toString(), role: 'user', content: message },
            assistantMsg
          ]
        };
        setActiveConversation(newConv);
        setConversations([newConv, ...conversations]);
      } else {
        const updatedConv = {
          ...activeConversation,
          title,
          messages: [
            ...activeConversation.messages,
            { id: Date.now().toString(), role: 'user', content: message },
            assistantMsg
          ]
        };
        setActiveConversation(updatedConv);
        setConversations(conversations.map(c => c.id === conversation_id ? updatedConv : c));
      }
    } catch (error) {
      toast.error('Failed to send message: ' + (error.response?.data?.detail || error.message));
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddWebhook = async (webhookData) => {
    try {
      const response = await axios.post(`${API}/webhooks`, webhookData);
      setWebhooks([...webhooks, response.data]);
      toast.success('Webhook created');
    } catch (error) {
      toast.error('Failed to create webhook');
    }
  };

  const handleDeleteWebhook = async (id) => {
    try {
      await axios.delete(`${API}/webhooks/${id}`);
      setWebhooks(webhooks.filter(w => w.id !== id));
      toast.success('Webhook deleted');
    } catch (error) {
      toast.error('Failed to delete webhook');
    }
  };

  const handleTestWebhook = async (id) => {
    try {
      const response = await axios.post(`${API}/webhooks/${id}/test`);
      if (response.data.status === 'success') {
        toast.success(`Webhook test successful (${response.data.response_code})`);
      } else {
        toast.error('Webhook test failed: ' + response.data.message);
      }
    } catch (error) {
      toast.error('Failed to test webhook');
    }
  };

  const handleAddAgent = async (agentData) => {
    try {
      const response = await axios.post(`${API}/swarm/agents`, agentData);
      setAgents([...agents, response.data]);
      toast.success('Agent created');
    } catch (error) {
      toast.error('Failed to create agent');
    }
  };

  const handleDeleteAgent = async (id) => {
    try {
      await axios.delete(`${API}/swarm/agents/${id}`);
      setAgents(agents.filter(a => a.id !== id));
      toast.success('Agent deleted');
    } catch (error) {
      toast.error('Failed to delete agent');
    }
  };

  const handleCreateTask = async (taskData) => {
    try {
      const response = await axios.post(`${API}/swarm/tasks`, taskData);
      setTasks([response.data, ...tasks]);
      toast.success('Task started');
      // Poll for task completion
      const pollTask = setInterval(async () => {
        try {
          const taskResponse = await axios.get(`${API}/swarm/tasks/${response.data.id}`);
          if (taskResponse.data.status !== 'running') {
            clearInterval(pollTask);
            setTasks(prev => prev.map(t => t.id === response.data.id ? taskResponse.data : t));
            if (taskResponse.data.status === 'completed') {
              toast.success('Task completed');
            }
          }
        } catch (e) {
          clearInterval(pollTask);
        }
      }, 2000);
    } catch (error) {
      toast.error('Failed to create task');
    }
  };

  const handleUpdateSettings = async (newSettings) => {
    try {
      await axios.put(`${API}/settings`, newSettings);
      setSettings(newSettings);
      toast.success('Settings saved');
    } catch (error) {
      toast.error('Failed to save settings');
    }
  };

  return (
    <div className="h-screen flex bg-background" data-testid="app-container">
      <Toaster position="top-right" theme="dark" />
      
      <Sidebar
        conversations={conversations}
        activeConversation={activeConversation}
        onSelectConversation={handleSelectConversation}
        onNewChat={handleNewChat}
        onDeleteConversation={handleDeleteConversation}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {activeTab === 'chat' && (
        <ChatInterface
          conversation={activeConversation}
          models={models}
          selectedModel={selectedModel}
          onSelectModel={setSelectedModel}
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      )}

      {activeTab === 'integrations' && (
        <IntegrationsPage
          webhooks={webhooks}
          onAddWebhook={handleAddWebhook}
          onDeleteWebhook={handleDeleteWebhook}
          onTestWebhook={handleTestWebhook}
        />
      )}

      {activeTab === 'swarm' && (
        <SwarmPage
          agents={agents}
          tasks={tasks}
          onAddAgent={handleAddAgent}
          onDeleteAgent={handleDeleteAgent}
          onCreateTask={handleCreateTask}
        />
      )}

      {activeTab === 'settings' && (
        <SettingsPage
          settings={settings}
          models={models}
          onUpdateSettings={handleUpdateSettings}
        />
      )}
    </div>
  );
}

export default App;
