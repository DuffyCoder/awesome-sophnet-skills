#!/usr/bin/env node

/**
 * 飞书电子表格命令行工具
 */

const { program } = require('commander');
const FeishuSheetsAPI = require('../src/api');
const { parseJsonInput, validateRequired } = require('../src/utils');

require('dotenv').config();

program
  .name('feishu-sheets')
  .description('飞书电子表格命令行工具')
  .version('1.0.0');

// 测试连接
program
  .command('test')
  .description('测试飞书连接')
  .action(async () => {
    try {
      const api = new FeishuSheetsAPI();
      const result = await api.testConnection();
      if (result.success) {
        console.log('✅ 连接测试成功');
        console.log(`应用ID: ${result.appId}`);
      } else {
        console.error('❌ 连接测试失败:', result.message);
        process.exit(1);
      }
    } catch (error) {
      console.error('❌ 连接测试失败:', error.message);
      process.exit(1);
    }
  });

// 创建电子表格
program
  .command('create-spreadsheet')
  .description('创建电子表格')
  .option('--title <title>', '表格标题')
  .option('--folder-token <token>', '目标文件夹token')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const result = await api.createSpreadsheet(options.title, options.folderToken);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 创建电子表格失败:', error.message);
      process.exit(1);
    }
  });

// 获取电子表格信息
program
  .command('get-spreadsheet')
  .description('获取电子表格信息')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const result = await api.getSpreadsheet(options.spreadsheetToken);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 获取电子表格信息失败:', error.message);
      process.exit(1);
    }
  });

// 列出工作表
program
  .command('list-sheets')
  .description('列出所有工作表')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const result = await api.listSheets(options.spreadsheetToken);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 列出工作表失败:', error.message);
      process.exit(1);
    }
  });

// 获取工作表信息
program
  .command('get-sheet')
  .description('获取工作表信息')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--sheet-id <id>', '工作表ID')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const result = await api.getSheet(options.spreadsheetToken, options.sheetId);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 获取工作表信息失败:', error.message);
      process.exit(1);
    }
  });

// 添加工作表
program
  .command('add-sheet')
  .description('添加工作表')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--title <title>', '工作表标题')
  .option('--index <number>', '插入位置索引')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const index = options.index !== undefined ? parseInt(options.index) : undefined;
      const result = await api.addSheet(options.spreadsheetToken, options.title, index);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 添加工作表失败:', error.message);
      process.exit(1);
    }
  });

// 删除工作表
program
  .command('delete-sheet')
  .description('删除工作表')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--sheet-id <id>', '工作表ID')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const result = await api.deleteSheet(options.spreadsheetToken, options.sheetId);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 删除工作表失败:', error.message);
      process.exit(1);
    }
  });

// 读取单元格数据
program
  .command('read')
  .description('读取单元格数据')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--range <range>', '范围，格式: sheetId!A1:C5')
  .option('--value-render <type>', '值渲染方式: ToString/FormattedValue/UnformattedValue')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const params = {};
      if (options.valueRender) params.valueRenderOption = options.valueRender;
      const result = await api.readRange(options.spreadsheetToken, options.range, params);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 读取数据失败:', error.message);
      process.exit(1);
    }
  });

// 写入单元格数据
program
  .command('write')
  .description('写入单元格数据')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--range <range>', '范围，格式: sheetId!A1:C5')
  .requiredOption('--values <json>', '二维数组JSON或@文件路径')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const values = parseJsonInput(options.values);
      if (!Array.isArray(values)) {
        throw new Error('--values 必须是二维数组');
      }
      const result = await api.writeRange(options.spreadsheetToken, options.range, values);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 写入数据失败:', error.message);
      process.exit(1);
    }
  });

// 追加数据
program
  .command('append')
  .description('在有数据的范围之后追加数据')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--range <range>', '范围')
  .requiredOption('--values <json>', '二维数组JSON或@文件路径')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const values = parseJsonInput(options.values);
      const result = await api.appendData(options.spreadsheetToken, options.range, values);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 追加数据失败:', error.message);
      process.exit(1);
    }
  });

// 前置插入数据
program
  .command('prepend')
  .description('在范围开头前插入数据')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--range <range>', '范围')
  .requiredOption('--values <json>', '二维数组JSON或@文件路径')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const values = parseJsonInput(options.values);
      const result = await api.prependData(options.spreadsheetToken, options.range, values);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 前置插入失败:', error.message);
      process.exit(1);
    }
  });

// 批量读取
program
  .command('batch-read')
  .description('批量读取多个范围')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--ranges <ranges>', '范围列表，逗号分隔: sheetId!A1:C5,sheetId!D1:F5')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const ranges = options.ranges.split(',').map(r => r.trim());
      const result = await api.batchGetValues(options.spreadsheetToken, ranges);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 批量读取失败:', error.message);
      process.exit(1);
    }
  });

// 批量写入
program
  .command('batch-write')
  .description('批量写入多个范围')
  .requiredOption('--spreadsheet-token <token>', '电子表格token')
  .requiredOption('--data <json>', '数据JSON: [{range, values}]')
  .action(async (options) => {
    try {
      const api = new FeishuSheetsAPI();
      const valueRanges = parseJsonInput(options.data);
      if (!Array.isArray(valueRanges)) {
        throw new Error('--data 必须是数组格式 [{range, values}]');
      }
      const result = await api.batchUpdateValues(options.spreadsheetToken, valueRanges);
      console.log(JSON.stringify(result, null, 2));
    } catch (error) {
      console.error('❌ 批量写入失败:', error.message);
      process.exit(1);
    }
  });

if (!process.argv.slice(2).length) {
  program.outputHelp();
} else {
  program.parse(process.argv);
}
