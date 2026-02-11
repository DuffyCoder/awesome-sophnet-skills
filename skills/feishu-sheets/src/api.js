/**
 * 飞书电子表格 (Sheets) API 客户端
 * 注意：电子表格同时使用 v2 和 v3 两个版本的API
 * - v3: 表格元信息、工作表管理
 * - v2: 单元格数据读写
 */

const axios = require('axios');
const { getEnvVar, getAccessToken, validateRequired, delay } = require('./utils');

class FeishuSheetsAPI {
  constructor(options = {}) {
    this.appId = options.appId || getEnvVar('FEISHU_APP_ID');
    this.appSecret = options.appSecret || getEnvVar('FEISHU_APP_SECRET') || getEnvVar('FEISHU_APP_SECRET_PATH');
    this.accessToken = options.accessToken;

    if (!this.appId || !this.appSecret) {
      throw new Error('缺少FEISHU_APP_ID或FEISHU_APP_SECRET环境变量');
    }

    // v3 客户端 - 表格元信息和工作表管理
    this.clientV3 = this._createClient('https://open.feishu.cn/open-apis/sheets/v3');
    // v2 客户端 - 单元格数据读写
    this.clientV2 = this._createClient('https://open.feishu.cn/open-apis/sheets/v2');
  }

  _createClient(baseURL) {
    const client = axios.create({
      baseURL,
      timeout: 30000,
      headers: { 'Content-Type': 'application/json; charset=utf-8' }
    });

    client.interceptors.request.use(async (config) => {
      if (!this.accessToken) {
        await this.refreshAccessToken();
      }
      config.headers.Authorization = `Bearer ${this.accessToken}`;
      return config;
    });

    client.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        if (error.response && error.response.data && error.response.data.code === 99991663 && !originalRequest._retry) {
          originalRequest._retry = true;
          try {
            await this.refreshAccessToken();
            originalRequest.headers.Authorization = `Bearer ${this.accessToken}`;
            return client(originalRequest);
          } catch (refreshError) {
            return Promise.reject(refreshError);
          }
        }
        return Promise.reject(error);
      }
    );

    return client;
  }

  async refreshAccessToken() {
    this.accessToken = await getAccessToken(this.appId, this.appSecret);
    return this.accessToken;
  }

  // ============ 表格元信息 (v3) ============

  /**
   * 创建电子表格
   * @param {string} title - 表格标题
   * @param {string} folderToken - 可选，目标文件夹token
   */
  async createSpreadsheet(title, folderToken) {
    try {
      const body = {};
      if (title) body.title = title;
      if (folderToken) body.folder_token = folderToken;
      const response = await this.clientV3.post('/spreadsheets', body);
      return response.data;
    } catch (error) {
      throw this.handleError(error, '创建电子表格');
    }
  }

  /**
   * 获取电子表格信息
   */
  async getSpreadsheet(spreadsheetToken) {
    validateRequired({ spreadsheetToken }, ['spreadsheetToken']);
    try {
      const response = await this.clientV3.get(`/spreadsheets/${spreadsheetToken}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, '获取电子表格信息');
    }
  }

  /**
   * 获取工作表列表
   */
  async listSheets(spreadsheetToken) {
    validateRequired({ spreadsheetToken }, ['spreadsheetToken']);
    try {
      const response = await this.clientV3.get(`/spreadsheets/${spreadsheetToken}/sheets/query`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, '获取工作表列表');
    }
  }

  /**
   * 获取单个工作表信息
   */
  async getSheet(spreadsheetToken, sheetId) {
    validateRequired({ spreadsheetToken, sheetId }, ['spreadsheetToken', 'sheetId']);
    try {
      const response = await this.clientV3.get(`/spreadsheets/${spreadsheetToken}/sheets/${sheetId}`);
      return response.data;
    } catch (error) {
      throw this.handleError(error, '获取工作表信息');
    }
  }

  // ============ 工作表操作 (v2) ============

  /**
   * 操作工作表（增删改）
   * @param {string} spreadsheetToken
   * @param {object} requests - 操作请求体
   */
  async batchUpdateSheets(spreadsheetToken, requests) {
    validateRequired({ spreadsheetToken }, ['spreadsheetToken']);
    try {
      const response = await this.clientV2.post(`/spreadsheets/${spreadsheetToken}/sheets_batch_update`, {
        requests
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, '操作工作表');
    }
  }

  /**
   * 添加工作表
   */
  async addSheet(spreadsheetToken, title, index) {
    const requests = [{
      addSheet: {
        properties: {
          title,
          ...(index !== undefined ? { index } : {})
        }
      }
    }];
    return this.batchUpdateSheets(spreadsheetToken, requests);
  }

  /**
   * 删除工作表
   */
  async deleteSheet(spreadsheetToken, sheetId) {
    const requests = [{
      deleteSheet: { sheetId }
    }];
    return this.batchUpdateSheets(spreadsheetToken, requests);
  }

  // ============ 单元格数据操作 (v2) ============

  /**
   * 读取单元格数据
   * @param {string} spreadsheetToken
   * @param {string} range - 范围，格式: sheetId!A1:C5 或 sheetName!A1:C5
   */
  async readRange(spreadsheetToken, range, params = {}) {
    validateRequired({ spreadsheetToken, range }, ['spreadsheetToken', 'range']);
    try {
      const response = await this.clientV2.get(
        `/spreadsheets/${spreadsheetToken}/values/${encodeURIComponent(range)}`,
        { params }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, '读取单元格数据');
    }
  }

  /**
   * 写入单元格数据
   * @param {string} spreadsheetToken
   * @param {string} range - 范围
   * @param {Array<Array>} values - 二维数组
   */
  async writeRange(spreadsheetToken, range, values) {
    validateRequired({ spreadsheetToken, range }, ['spreadsheetToken', 'range']);
    try {
      const response = await this.clientV2.put(`/spreadsheets/${spreadsheetToken}/values`, {
        valueRange: {
          range,
          values
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, '写入单元格数据');
    }
  }

  /**
   * 追加数据（在有数据的范围之后追加）
   * @param {string} spreadsheetToken
   * @param {string} range - 范围
   * @param {Array<Array>} values - 二维数组
   */
  async appendData(spreadsheetToken, range, values) {
    validateRequired({ spreadsheetToken, range }, ['spreadsheetToken', 'range']);
    try {
      const response = await this.clientV2.post(`/spreadsheets/${spreadsheetToken}/values_append`, {
        valueRange: {
          range,
          values
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, '追加数据');
    }
  }

  /**
   * 前置插入数据
   */
  async prependData(spreadsheetToken, range, values) {
    validateRequired({ spreadsheetToken, range }, ['spreadsheetToken', 'range']);
    try {
      const response = await this.clientV2.post(`/spreadsheets/${spreadsheetToken}/values_prepend`, {
        valueRange: {
          range,
          values
        }
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, '前置插入数据');
    }
  }

  /**
   * 批量读取多个范围
   * @param {string} spreadsheetToken
   * @param {Array<string>} ranges - 范围数组
   */
  async batchGetValues(spreadsheetToken, ranges, params = {}) {
    validateRequired({ spreadsheetToken }, ['spreadsheetToken']);
    try {
      const response = await this.clientV2.get(
        `/spreadsheets/${spreadsheetToken}/values_batch_get`,
        {
          params: {
            ...params,
            ranges: ranges.join(',')
          }
        }
      );
      return response.data;
    } catch (error) {
      throw this.handleError(error, '批量读取数据');
    }
  }

  /**
   * 批量写入多个范围
   * @param {string} spreadsheetToken
   * @param {Array} valueRanges - [{range, values}] 数组
   */
  async batchUpdateValues(spreadsheetToken, valueRanges) {
    validateRequired({ spreadsheetToken }, ['spreadsheetToken']);
    try {
      const response = await this.clientV2.post(`/spreadsheets/${spreadsheetToken}/values_batch_update`, {
        valueRanges
      });
      return response.data;
    } catch (error) {
      throw this.handleError(error, '批量写入数据');
    }
  }

  // ============ 工具方法 ============

  handleError(error, operation) {
    if (error.response) {
      const { status, data } = error.response;
      const errorMsg = data.msg || data.message || error.message;
      const fullError = new Error(`${operation}失败: ${errorMsg} (状态码: ${status})`);
      fullError.status = status;
      fullError.data = data;
      return fullError;
    } else if (error.request) {
      return new Error(`${operation}失败: 网络错误，无法连接到飞书服务器`);
    } else {
      return new Error(`${operation}失败: ${error.message}`);
    }
  }

  async testConnection() {
    try {
      await this.refreshAccessToken();
      return {
        success: true,
        message: '连接测试成功',
        appId: this.appId,
        tokenValid: !!this.accessToken
      };
    } catch (error) {
      return {
        success: false,
        message: `连接测试失败: ${error.message}`,
        appId: this.appId
      };
    }
  }
}

module.exports = FeishuSheetsAPI;
