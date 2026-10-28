#ifndef PEN_UPDATE_POLICY_H
#define PEN_UPDATE_POLICY_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#define PEN_UPDATE_REQUIRED_TESTS UINT32_C(31) /* storage, protocol, power, contact, camera */
typedef struct {
 bool authorized, contact_up, power_qualified, storage_durable, recording_idle;
} pen_update_safety;
typedef struct {
 uint32_t bytes, version;
 char project[32], hardware[32];
 uint8_t sha256[32];
} pen_update_manifest;
typedef struct {
 uint32_t minimum_version, running_version, partition_bytes;
 const char *project, *hardware;
 bool enabled, signatures_enforced, rollback_enabled, pending_verify;
} pen_update_policy;
typedef enum { PEN_UPDATE_IDLE, PEN_UPDATE_WRITING, PEN_UPDATE_READY, PEN_UPDATE_FAILED } pen_update_state;
typedef struct { pen_update_state state; uint32_t expected_bytes, received, version; } pen_update_transaction;
/* Signed esp_app_desc.version must be canonical decimal PROJECT_VER, <=u32. */
int pen_update_version_parse(const char text[32],uint32_t *version);
bool pen_update_safe(const pen_update_safety *s);
int pen_update_start(pen_update_transaction *t,const pen_update_policy *p,const pen_update_manifest *m,const pen_update_safety *s);
int pen_update_chunk(pen_update_transaction *t,uint32_t offset,size_t bytes,const pen_update_safety *s);
int pen_update_finish(pen_update_transaction *t,bool digest_ok,bool signature_and_descriptor_ok,const pen_update_safety *s);
/* Mark-valid is forbidden until every required measured diagnostic passed. */
bool pen_update_boot_healthy(uint32_t passed_tests,const pen_update_safety *s);
#endif
