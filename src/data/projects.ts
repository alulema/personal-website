export type ProjectCategory = 'ai' | 'ml' | 'backend' | 'fullstack';
export type DemoStatus = 'offline' | 'pending' | 'active';

export interface Project {
  id: string;
  title: string;
  titleEs: string;
  description: string;
  descriptionEs: string;
  techStack: string[];
  subdomain: string;
  githubUrl?: string;
  coverImage?: string;
  featured: boolean;
  category: ProjectCategory;
}

export const projects: Project[] = [
  {
    id: 'rag-demo',
    title: 'RAG Chatbot over Blog Posts',
    titleEs: 'Chatbot RAG sobre Posts del Blog',
    description:
      'An interactive retrieval-augmented generation chatbot that answers questions using my blog posts as a knowledge base. Built with Azure AI Search and LangChain.',
    descriptionEs:
      'Un chatbot interactivo de generación aumentada por recuperación que responde preguntas usando mis posts del blog como base de conocimiento. Construido con Azure AI Search y LangChain.',
    techStack: ['Python', 'FastAPI', 'LangChain', 'Azure AI Search', 'OpenAI API'],
    subdomain: 'rag.alexisalulema.com',
    featured: true,
    category: 'ai',
  },
  {
    id: 'bert-classifier',
    title: 'Text Classifier with BERT',
    titleEs: 'Clasificador de Texto con BERT',
    description:
      'Interactive demo of the BERT-based text classifier developed for the AOLME project at University of New Mexico. Compare BERT against BI-LSTM, SVM, and RandomForest.',
    descriptionEs:
      'Demo interactivo del clasificador de texto basado en BERT desarrollado para el proyecto AOLME en la Universidad de Nuevo México. Compara BERT con BI-LSTM, SVM y RandomForest.',
    techStack: ['Python', 'PyTorch', 'Transformers', 'FastAPI', 'Scikit-learn'],
    subdomain: 'bert.alexisalulema.com',
    githubUrl: 'https://github.com/alulema',
    featured: true,
    category: 'ml',
  },
  {
    id: 'agent-ai-demo',
    title: 'Multi-Agent AI Orchestration',
    titleEs: 'Orquestación Multi-Agente con IA',
    description:
      'A demo of multi-agent AI systems using LangGraph and Semantic Kernel. Agents collaborate to break down and solve complex tasks autonomously.',
    descriptionEs:
      'Un demo de sistemas multi-agente usando LangGraph y Semantic Kernel. Los agentes colaboran para descomponer y resolver tareas complejas de forma autónoma.',
    techStack: ['Python', 'LangGraph', 'Semantic Kernel', 'FastAPI', 'Azure OpenAI'],
    subdomain: 'agents.alexisalulema.com',
    featured: true,
    category: 'ai',
  },
  {
    id: 'fastapi-patterns',
    title: 'FastAPI Production Patterns',
    titleEs: 'Patrones de FastAPI en Producción',
    description:
      'A live reference implementation showcasing FastAPI best practices: async endpoints, dependency injection, JWT auth, rate limiting, and OpenTelemetry tracing.',
    descriptionEs:
      'Una implementación de referencia que muestra las mejores prácticas de FastAPI: endpoints async, inyección de dependencias, autenticación JWT, rate limiting y trazado con OpenTelemetry.',
    techStack: ['Python', 'FastAPI', 'PostgreSQL', 'Redis', 'Docker'],
    subdomain: 'fastapi.alexisalulema.com',
    githubUrl: 'https://github.com/alulema',
    featured: false,
    category: 'backend',
  },
];

export const categoryLabels: Record<ProjectCategory, { en: string; es: string }> = {
  ai:       { en: 'AI & LLM',       es: 'IA y LLM' },
  ml:       { en: 'Machine Learning', es: 'Machine Learning' },
  backend:  { en: 'Backend',         es: 'Backend' },
  fullstack:{ en: 'Full Stack',      es: 'Full Stack' },
};
