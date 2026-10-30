0000000000001220 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m>:
    1220:	test   %rdx,%rdx
    1223:	je     12a0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>
    1225:	mov    (%rsi),%rcx
    1228:	mov    (%rdi),%rsi
    122b:	mov    %edx,%eax
    122d:	and    $0x3,%eax
    1230:	cmp    $0x4,%rdx
    1234:	jae    123a <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x1a>
    1236:	xor    %edi,%edi
    1238:	jmp    127b <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x5b>
    123a:	and    $0xfffffffffffffffc,%rdx
    123e:	xor    %edi,%edi
    1240:	mov    (%rcx,%rdi,4),%r8d
    1244:	add    %r8d,%r8d
    1247:	mov    %r8d,(%rsi,%rdi,4)
    124b:	mov    0x4(%rcx,%rdi,4),%r8d
    1250:	add    %r8d,%r8d
    1253:	mov    %r8d,0x4(%rsi,%rdi,4)
    1258:	mov    0x8(%rcx,%rdi,4),%r8d
    125d:	add    %r8d,%r8d
    1260:	mov    %r8d,0x8(%rsi,%rdi,4)
    1265:	mov    0xc(%rcx,%rdi,4),%r8d
    126a:	add    %r8d,%r8d
    126d:	mov    %r8d,0xc(%rsi,%rdi,4)
    1272:	add    $0x4,%rdi
    1276:	cmp    %rdi,%rdx
    1279:	jne    1240 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x20>
    127b:	test   %rax,%rax
    127e:	je     12a0 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x80>
    1280:	lea    (%rsi,%rdi,4),%rdx
    1284:	lea    (%rcx,%rdi,4),%rcx
    1288:	xor    %esi,%esi
    128a:	nopw   0x0(%rax,%rax,1)
    1290:	mov    (%rcx,%rsi,4),%edi
    1293:	add    %edi,%edi
    1295:	mov    %edi,(%rdx,%rsi,4)
    1298:	inc    %rsi
    129b:	cmp    %rsi,%rax
    129e:	jne    1290 <_Z16kern_t04_scale_nRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_m+0x70>
    12a0:	ret
    12a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
