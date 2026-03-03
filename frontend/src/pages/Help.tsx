import React from 'react';
import { Card, Typography, Divider, List } from 'antd';
import '../styles/common.scss';

const { Title, Paragraph, Text } = Typography;

// 帮助文档页面组件
const Help: React.FC = () => {
  return (
    <div>
      <Title level={2}>帮助文档</Title>
      
      <Card title="系统简介" style={{ marginBottom: 16 }}>
        <Paragraph>
          课题组资产管理系统（Lab Asset Management，简称LAM）是一个专为科研课题组设计的资产管理系统。
          系统旨在通过信息化手段，实现资产的全生命周期管理，提高管理效率，降低管理成本。
        </Paragraph>
        <Paragraph>
          系统主要功能包括：资产管理、耗材管理、采购管理、资产借用、领料管理、资产转移、统计分析等。
        </Paragraph>
      </Card>

      <Card title="功能模块说明" style={{ marginBottom: 16 }}>
        <List
          dataSource={[
            {
              title: '资产管理',
              description: '管理课题组所有仪器设备、试剂等固定资产，包括资产的添加、编辑、删除、查看等功能。'
            },
            {
              title: '耗材管理',
              'description': '管理实验过程中消耗的材料、试剂等，支持库存预警功能。'
            },
            {
              title: '采购管理',
              description: '用户可以提交采购申请，管理员进行审批，实现采购流程的规范化管理。'
            },
            {
              title: '资产借用',
              description: '用户可以借用可用状态的资产，使用完毕后归还，系统自动记录借用历史。'
            },
            {
              title: '领料管理',
              description: '用户可以申请领用耗材，管理员审批后扣减库存，确保耗材使用的可追溯性。'
            },
            {
              title: '资产转移',
              description: '用户可以申请将资产从一个位置转移到另一个位置，管理员审批后执行转移。'
            },
            {
              title: '统计分析',
              description: '提供各类统计数据，包括资产按状态/类别统计、耗材总价值、采购预算等，辅助决策。'
            },
            {
              title: '操作日志',
              description: '记录系统所有操作，管理员可以查看操作历史，便于审计和问题追踪。'
            },
          ]}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={<Text strong>{item.title}</Text>}
                description={item.description}
              />
            </List.Item>
          )}
        />
      </Card>

      <Card title="操作指南" style={{ marginBottom: 16 }}>
        <Title level={4}>用户登录</Title>
        <Paragraph>
          首次使用需要注册账号，注册成功后自动登录。已注册用户可以直接使用用户名和密码登录系统。
        </Paragraph>

        <Divider />

        <Title level={4}>借用资产</Title>
        <Paragraph>
          1. 进入"资产借用"页面<br />
          2. 点击"借用资产"按钮<br />
          3. 选择要借用的资产（仅显示可用状态的资产）<br />
          4. 填写用途（可选）<br />
          5. 提交申请，系统自动批准<br />
          6. 使用完毕后，在"我的借用记录"中点击"归还"按钮
        </Paragraph>

        <Divider />

        <Title level={4}>提交采购申请</Title>
        <Paragraph>
          1. 进入"采购管理"页面<br />
          2. 点击"提交采购申请"按钮<br />
          3. 填写采购标题、物品名称、数量、预算等信息<br />
          4. 选择供应商（可选）<br />
          5. 填写采购原因<br />
          6. 提交申请，等待管理员审批
        </Paragraph>

        <Divider />

        <Title level={4}>领用耗材</Title>
        <Paragraph>
          1. 进入"领料管理"页面<br />
          2. 点击"提交领料申请"按钮<br />
          3. 选择要领用的耗材（仅显示库存大于0的耗材）<br />
          4. 填写领用数量（不能超过当前库存）<br />
          5. 填写用途（可选）<br />
          6. 提交申请，等待管理员审批
        </Paragraph>

        <Divider />

        <Title level={4}>资产转移</Title>
        <Paragraph>
          1. 进入"资产转移"页面<br />
          2. 点击"提交转移申请"按钮<br />
          3. 选择要转移的资产<br />
          4. 填写新位置<br />
          5. 填写转移原因<br />
          6. 提交申请，等待管理员审批
        </Paragraph>
      </Card>

      <Card title="常见问题解答" style={{ marginBottom: 16 }}>
        <List
          dataSource={[
            {
              q: '如何修改密码？',
              a: '目前系统暂不支持在线修改密码功能，如需修改密码请联系管理员。'
            },
            {
              q: '为什么无法借用某个资产？',
              a: '只有状态为"可用"的资产才能被借用。如果资产状态为"使用中"、"维修中"或"已报废"，则无法借用。'
            },
            {
              q: '库存预警是什么意思？',
              a: '当耗材的当前库存低于设置的最低库存时，系统会显示预警提示，提醒管理员及时补充库存。'
            },
            {
              q: '采购申请被拒绝了怎么办？',
              a: '采购申请被拒绝后，可以查看拒绝原因，并根据实际情况重新提交申请。'
            },
            {
              q: '管理员有哪些特殊权限？',
              a: '管理员拥有所有功能的完全访问权限，包括：审批采购/领料/转移申请、添加/编辑/删除资产和耗材、查看操作日志等。'
            },
          ]}
          renderItem={(item) => (
            <List.Item>
              <List.Item.Meta
                title={<Text strong>Q: {item.q}</Text>}
                description={<Text>A: {item.a}</Text>}
              />
            </List.Item>
          )}
        />
      </Card>

      <Card title="联系支持">
        <Paragraph>
          如果您在使用过程中遇到问题或有任何建议，请联系系统管理员或技术支持团队。
        </Paragraph>
        <Paragraph>
          <Text strong>技术支持：</Text> support@example.com<br />
          <Text strong>联系电话：</Text> 400-XXX-XXXX
        </Paragraph>
      </Card>
    </div>
  );
};

export default Help;
