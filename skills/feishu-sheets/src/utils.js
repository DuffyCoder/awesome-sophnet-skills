/**
 * 飞书通用工具函数
 */

const fs = require('fs');
const path = require('path');

function getEnvVar(name, defaultValue = null) {
  let value = process.env[name];
  if (name.endsWith('_PATH') && value) {
    try {
      const filePath = value.startsWith('~')
        ? path.join(process.env.HOME, value.slice(1))
        : value;
      if (fs.existsSync(filePath)) {
        value = fs.readFileSync(filePath, 'utf8').trim();
      }
    } catch (error) {
      console.warn(`无法读取文件 ${value}: ${error.message}`);
    }
  }
  return value || defaultValue;
}

async function getAccessToken(appId, appSecret) {
  const axios = require('axios');
  try {
    const response = await axios.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/', {
      app_id: appId,
      app_secret: appSecret
    }, {
      headers: { 'Content-Type': 'application/json; charset=utf-8' }
    });
    if (response.data.code === 0) {
      return response.data.tenant_access_token;
    } else {
      throw new Error(`获取访问令牌失败: ${response.data.msg}`);
    }
  } catch (error) {
    throw new Error(`获取访问令牌时出错: ${error.message}`);
  }
}

function validateRequired(params, requiredFields) {
  for (const field of requiredFields) {
    if (!params[field]) {
      throw new Error(`缺少必填参数: ${field}`);
    }
  }
}

function parseJsonInput(input) {
  if (!input) return null;
  if (typeof input === 'string' && input.startsWith('@')) {
    const filePath = input.slice(1);
    try {
      const content = fs.readFileSync(filePath, 'utf8');
      return JSON.parse(content);
    } catch (error) {
      throw new Error(`无法读取或解析文件 ${filePath}: ${error.message}`);
    }
  }
  if (typeof input === 'string') {
    try {
      return JSON.parse(input);
    } catch (error) {
      return input;
    }
  }
  return input;
}

function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

module.exports = {
  getEnvVar,
  getAccessToken,
  validateRequired,
  parseJsonInput,
  delay
};
