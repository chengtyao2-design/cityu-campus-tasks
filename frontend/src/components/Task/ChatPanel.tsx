import React, { useState, useEffect, useRef } from 'react';
import { Input, Button, Avatar, Tag, Modal, List, Empty, Spin } from 'antd';
import { 
  SendOutlined, 
  RobotOutlined, 
  UserOutlined,
  EnvironmentOutlined,
  BulbOutlined,
  LinkOutlined,

} from '@ant-design/icons';
import { TaskLocation, getCategoryColor, seedTasks } from '../../data/seedTasks';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  citations?: Citation[];
  suggestions?: TaskSuggestion[];
}

interface Citation {
  id: string;
  text: string;
  source: string;
  confidence: number;
}

interface TaskSuggestion {
  task: TaskLocation;
  reason: string;
  relevance: number;
}

interface ChatPanelProps {
  taskId: string;
  task: TaskLocation;
  onOpenOnMap: (task: TaskLocation) => void;
}

const { TextArea } = Input;

const ChatPanel: React.FC<ChatPanelProps> = ({ taskId: _taskId, task, onOpenOnMap }) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestionsModalOpen, setSuggestionsModalOpen] = useState(false);
  const [currentSuggestions, setCurrentSuggestions] = useState<TaskSuggestion[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Initialize with welcome message
    const welcomeMessage: Message = {
      id: 'welcome',
      type: 'assistant',
      content: `你好！我是任务助手，可以帮你了解"${task.title}"的相关信息。你可以问我关于任务的详情、位置、要求或者相关建议。`,
      timestamp: new Date(),
    };
    setMessages([welcomeMessage]);
  }, [task.title]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const generateMockResponse = (userInput: string): Message => {
    const input = userInput.toLowerCase();
    let content = '';
    let citations: Citation[] = [];
    let suggestions: TaskSuggestion[] = [];

    // Mock AI responses based on input keywords
    if (input.includes('位置') || input.includes('地点') || input.includes('在哪')) {
      content = `${task.title}位于${task.location.name}。这是CityU校园内的一个重要位置，你可以通过校园地图轻松找到。`;
      citations = [
        {
          id: 'loc1',
          text: `任务位置: ${task.location.name}`,
          source: '任务数据库',
          confidence: 0.95
        }
      ];
    } else if (input.includes('难度') || input.includes('困难')) {
      const difficultyText = task.difficulty === 'easy' ? '简单' : task.difficulty === 'medium' ? '中等' : '困难';
      content = `这个任务的难度等级是${difficultyText}。${
        task.difficulty === 'easy' ? '适合新手完成，不需要特殊技能。' :
        task.difficulty === 'medium' ? '需要一定的经验和技能，建议有相关基础再尝试。' :
        '这是一个高难度任务，需要丰富的经验和专业技能。'
      }`;
      citations = [
        {
          id: 'diff1',
          text: `难度等级: ${difficultyText}`,
          source: '任务评估系统',
          confidence: 0.98
        }
      ];
    } else if (input.includes('时间') || input.includes('多久')) {
      content = task.estimatedTime 
        ? `根据历史数据，完成这个任务大约需要${task.estimatedTime}分钟。实际时间可能因个人能力而有所不同。`
        : '这个任务没有明确的时间估算，建议根据任务复杂度合理安排时间。';
      if (task.estimatedTime) {
        citations = [
          {
            id: 'time1',
            text: `预计用时: ${task.estimatedTime}分钟`,
            source: '历史完成数据',
            confidence: 0.85
          }
        ];
      }
    } else if (input.includes('奖励') || input.includes('收获')) {
      content = task.rewards && task.rewards.length > 0
        ? `完成这个任务你将获得: ${task.rewards.join('、')}。这些奖励将帮助你在校园任务系统中获得更高的等级和声誉。`
        : '这个任务目前没有明确的奖励信息，但完成任务本身就是很好的学习和成长机会。';
      if (task.rewards && task.rewards.length > 0) {
        citations = task.rewards.map((reward, index) => ({
          id: `reward${index}`,
          text: reward,
          source: '奖励系统',
          confidence: 0.92
        }));
      }
    } else if (input.includes('建议') || input.includes('推荐') || input.includes('相关')) {
      content = '基于你当前的任务，我为你推荐了一些相关的任务。这些任务可能与你的兴趣或技能相匹配。';
      
      // Generate task suggestions
      const relatedTasks = seedTasks
        .filter(t => t.task_id !== task.task_id)
        .filter(t => 
          t.category === task.category || 
          t.difficulty === task.difficulty ||
          t.course === task.course
        )
        .slice(0, 3)
        .map(t => ({
          task: t,
          reason: t.category === task.category 
            ? `同属${t.category}类别` 
            : t.difficulty === task.difficulty 
            ? `相同难度等级` 
            : `同一课程: ${t.course}`,
          relevance: Math.random() * 0.3 + 0.7 // 0.7-1.0
        }));

      suggestions = relatedTasks;
      setCurrentSuggestions(relatedTasks);
    } else {
      // Default response with no evidence
      content = '抱歉，我没有找到与你问题相关的具体信息。你可以尝试询问任务的位置、难度、时间要求或奖励等具体方面。';
      citations = [];
    }

    return {
      id: Date.now().toString(),
      type: 'assistant',
      content,
      timestamp: new Date(),
      citations: citations.length > 0 ? citations : undefined,
      suggestions: suggestions.length > 0 ? suggestions : undefined
    };
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate API delay
    setTimeout(() => {
      const assistantMessage = generateMockResponse(inputValue);
      setMessages(prev => [...prev, assistantMessage]);
      setIsLoading(false);
    }, 1000 + Math.random() * 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const openSuggestionsModal = (suggestions: TaskSuggestion[]) => {
    setCurrentSuggestions(suggestions);
    setSuggestionsModalOpen(true);
  };

  const handleTaskSuggestionClick = (suggestedTask: TaskLocation) => {
    setSuggestionsModalOpen(false);
    onOpenOnMap(suggestedTask);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4 max-h-96">
        {messages.map((message) => (
          <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`flex gap-2 max-w-[80%] ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}>
              <Avatar 
                icon={message.type === 'user' ? <UserOutlined /> : <RobotOutlined />}
                className={message.type === 'user' ? 'bg-blue-500' : 'bg-green-500'}
              />
              <div className="space-y-2">
                <div 
                  className={`px-3 py-2 rounded-lg ${
                    message.type === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-100 text-gray-800'
                  }`}
                >
                  {message.content}
                </div>
                
                {/* Citations */}
                {message.citations && message.citations.length > 0 && (
                  <div className="space-y-1">
                    <div className="text-xs text-gray-500 flex items-center gap-1">
                      <LinkOutlined />
                      引用来源:
                    </div>
                    {message.citations.map((citation) => (
                      <div key={citation.id} className="text-xs bg-blue-50 p-2 rounded border-l-2 border-blue-200">
                        <div className="font-medium">{citation.text}</div>
                        <div className="text-gray-500 mt-1">
                          来源: {citation.source} | 可信度: {(citation.confidence * 100).toFixed(0)}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Task Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="space-y-2">
                    <Button 
                      type="link" 
                      size="small" 
                      icon={<BulbOutlined />}
                      onClick={() => openSuggestionsModal(message.suggestions!)}
                      className="p-0 h-auto"
                    >
                      查看相关任务推荐 ({message.suggestions.length})
                    </Button>
                  </div>
                )}

                <div className="text-xs text-gray-400">
                  {message.timestamp.toLocaleTimeString('zh-CN', { 
                    hour: '2-digit', 
                    minute: '2-digit' 
                  })}
                </div>
              </div>
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="flex justify-start">
            <div className="flex gap-2">
              <Avatar icon={<RobotOutlined />} className="bg-green-500" />
              <div className="bg-gray-100 px-3 py-2 rounded-lg">
                <Spin size="small" />
                <span className="ml-2 text-gray-600">正在思考...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="border-t pt-4">
        <div className="flex gap-2">
          <TextArea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="询问任务相关问题..."
            autoSize={{ minRows: 1, maxRows: 3 }}
            className="flex-1"
          />
          <Button 
            type="primary" 
            icon={<SendOutlined />}
            onClick={handleSendMessage}
            disabled={!inputValue.trim() || isLoading}
          />
        </div>
        <div className="text-xs text-gray-500 mt-2">
          按 Enter 发送，Shift + Enter 换行
        </div>
      </div>

      {/* Task Suggestions Modal */}
      <Modal
        title={
          <div className="flex items-center gap-2">
            <BulbOutlined className="text-orange-500" />
            相关任务推荐
          </div>
        }
        open={suggestionsModalOpen}
        onCancel={() => setSuggestionsModalOpen(false)}
        footer={null}
        width={600}
      >
        {currentSuggestions.length > 0 ? (
          <List
            dataSource={currentSuggestions}
            renderItem={(suggestion) => (
              <List.Item
                actions={[
                  <Button 
                    type="link" 
                    icon={<EnvironmentOutlined />}
                    onClick={() => handleTaskSuggestionClick(suggestion.task)}
                  >
                    在地图上查看
                  </Button>
                ]}
              >
                <List.Item.Meta
                  title={
                    <div className="flex items-center gap-2">
                      <div 
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: getCategoryColor(suggestion.task.category) }}
                      />
                      {suggestion.task.title}
                    </div>
                  }
                  description={
                    <div className="space-y-2">
                      <p className="text-gray-600">{suggestion.task.description}</p>
                      <div className="flex items-center gap-2">
                        <Tag color={getCategoryColor(suggestion.task.category)}>
                          {suggestion.task.category}
                        </Tag>
                        <Tag>
                          {suggestion.task.difficulty === 'easy' && '⭐ 简单'}
                          {suggestion.task.difficulty === 'medium' && '⭐⭐ 中等'}
                          {suggestion.task.difficulty === 'hard' && '⭐⭐⭐ 困难'}
                        </Tag>
                        <span className="text-sm text-gray-500">
                          推荐理由: {suggestion.reason}
                        </span>
                      </div>
                    </div>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无相关任务推荐" />
        )}
      </Modal>
    </div>
  );
};

export default ChatPanel;