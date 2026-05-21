import axios from 'axios';
import { getAuthHeaders } from './userApi';

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8080';

export interface QaPost {
  id: number;
  title: string;
  authorName: string;
  authorProfileImage: string | null;
  createdAt: string;
  commentCount: number;
}

export interface QaComment {
  id: number;
  postId: number;
  content: string;
  authorId: number;
  authorName: string;
  authorProfileImage: string | null;
  createdAt: string;
  updatedAt: string;
}

export interface QaPostDetail {
  id: number;
  title: string;
  content: string;
  authorId: number;
  authorName: string;
  authorProfileImage: string | null;
  createdAt: string;
  updatedAt: string;
  comments: QaComment[];
}

export interface PageResponse<T> {
  content: T[];
  totalPages: number;
  totalElements: number;
  size: number;
  number: number;
}

export const qaService = {
  getPosts: async (spaceId: number, page: number = 0): Promise<PageResponse<QaPost>> => {
    const response = await axios.get(`${API_BASE}/api/v1/qa/posts`, {
      params: { spaceId, page, size: 15 },
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  getPost: async (id: number): Promise<QaPostDetail> => {
    const response = await axios.get(`${API_BASE}/api/v1/qa/posts/${id}`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  },

  createPost: async (spaceId: number, title: string, content: string): Promise<QaPost> => {
    const response = await axios.post(
      `${API_BASE}/api/v1/qa/posts?spaceId=${spaceId}`,
      { title, content },
      { headers: getAuthHeaders() }
    );
    return response.data;
  },

  updatePost: async (id: number, title: string, content: string): Promise<QaPostDetail> => {
    const response = await axios.put(
      `${API_BASE}/api/v1/qa/posts/${id}`,
      { title, content },
      { headers: getAuthHeaders() }
    );
    return response.data;
  },

  deletePost: async (id: number): Promise<void> => {
    await axios.delete(`${API_BASE}/api/v1/qa/posts/${id}`, {
      headers: getAuthHeaders(),
    });
  },

  createComment: async (postId: number, content: string): Promise<QaComment> => {
    const response = await axios.post(
      `${API_BASE}/api/v1/qa/posts/${postId}/comments`,
      { content },
      { headers: getAuthHeaders() }
    );
    return response.data;
  },

  updateComment: async (commentId: number, content: string): Promise<QaComment> => {
    const response = await axios.put(
      `${API_BASE}/api/v1/qa/comments/${commentId}`,
      { content },
      { headers: getAuthHeaders() }
    );
    return response.data;
  },

  deleteComment: async (commentId: number): Promise<void> => {
    await axios.delete(`${API_BASE}/api/v1/qa/comments/${commentId}`, {
      headers: getAuthHeaders(),
    });
  },
};
