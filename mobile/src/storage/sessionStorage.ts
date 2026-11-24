import * as SecureStore from "expo-secure-store";
import { UserProfile } from "../types/domain";

const TOKEN_KEY = "arimms_mobile_access_token_v1";
const USER_KEY = "arimms_mobile_user_profile_v1";

let memoryToken: string | null = null;
let memoryUser: UserProfile | null = null;

async function safeGet(key: string): Promise<string | null> {
  try {
    if (await SecureStore.isAvailableAsync()) {
      return await SecureStore.getItemAsync(key);
    }
  } catch {
    // Fallback sang bộ nhớ tạm nếu thiết bị/môi trường không hỗ trợ SecureStore
  }
  if (key === TOKEN_KEY) {
    return memoryToken;
  }
  return memoryUser ? JSON.stringify(memoryUser) : null;
}

async function safeSet(key: string, value: string): Promise<void> {
  try {
    if (await SecureStore.isAvailableAsync()) {
      await SecureStore.setItemAsync(key, value);
      return;
    }
  } catch {
    // Fallback sang bộ nhớ tạm
  }
  if (key === TOKEN_KEY) {
    memoryToken = value;
  }
}

async function safeDelete(key: string): Promise<void> {
  try {
    if (await SecureStore.isAvailableAsync()) {
      await SecureStore.deleteItemAsync(key);
    }
  } catch {
    // Bỏ qua lỗi khi xóa key không tồn tại
  }
  if (key === TOKEN_KEY) {
    memoryToken = null;
  }
  if (key === USER_KEY) {
    memoryUser = null;
  }
}

export const sessionStorage = {
  async getToken(): Promise<string | null> {
    return safeGet(TOKEN_KEY);
  },

  async setToken(token: string): Promise<void> {
    await safeSet(TOKEN_KEY, token);
  },

  async getCachedUser(): Promise<UserProfile | null> {
    const raw = await safeGet(USER_KEY);
    if (!raw) {
      return memoryUser;
    }
    try {
      return JSON.parse(raw) as UserProfile;
    } catch {
      return null;
    }
  },

  async setCachedUser(user: UserProfile): Promise<void> {
    memoryUser = user;
    await safeSet(USER_KEY, JSON.stringify(user));
  },

  async clearSession(): Promise<void> {
    memoryToken = null;
    memoryUser = null;
    await Promise.all([safeDelete(TOKEN_KEY), safeDelete(USER_KEY)]);
  },
};