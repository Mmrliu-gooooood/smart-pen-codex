# v2修订与复现链

v1 manifest：`34e3d6e0f923a28eded99483ea57d79e42bf990c2618e12cf268eda690ff4b26`。
v1源包：`smart_pen_pc_receiver_candidate_20261029_v1_frozen.tar.gz`，SHA256 `f9cb646d21abb29ebc731d8fd81eed1d7d36764c91475dfe069c25f4ee01c7c7`。
原v1目录及日志未改；本目录为独立v2，不覆盖独审失败证据。

独立review证据位于 `smart_pen_pc_receiver_review_20261029`：

| 缺陷 | v1实复现 | v2修正与新增测试 |
|---|---|---|
| schema触发器静默丢INSERT | BEFORE INSERT RAISE(IGNORE)，真实receiver mock发1ACK而DB0记录 | 完整schema对象/SQL/PRAGMA结构/PK/unique/index一致性；事务内复验；affected rows；提交前后唯一精确row；无trigger白名单。拒绝DROP/rewriter trigger、额外view/table/index、缺unique/错误键/类型/PK/check、TEMP影子、同key多行。 |
| 导出目标身份丢失 | 两个target、相同label/device/session/seq导出逐字节相同 | metadata持久source_namespace规范复合hash，全部事件携带；record_sha256；clone/reopen保持源，wrong target拒绝，同key不同内容合流拒绝。无新认证token。 |
| callback/消费时间混淆 | 第二条片跨2.103秒，因第一条commit阻塞消费者仍ACK两条 | callback捕获单调观察时间，随队列传给reassembler；迟于2秒片拒绝，及时到达但晚持久化可正常处理。不是空口时间证明。 |

wire格式/UUID/精确ACK不变，NO_SENSOR不得进入评分不变。journal schema及NDJSON schema升为2，v1不自动迁移。
新增14个独立unittest（含参数化攻击变体），合计45项，无通过重复导入旧test class虚增计数。
回归继续覆盖COMMIT实际落盘后报告失败、post-COMMIT readback错误/缺行、取消/断连期间commit、已有行不完整重放不可ACK。
修订后仍需独立审查，不借此前v1“31 tests通过”替代新审查。

追加时钟负例：callback/重组器保留连接期单调最高观察时刻；中途10→11→10.5、NaN/Inf、fragment0或reset后的回退均fail closed。
接收器锁存clock fault，不把本条/后续记录ACK；此前已完成的有效ACK不撤回。新连接须新实例，绝不以dequeue时间“修正”时钟。
