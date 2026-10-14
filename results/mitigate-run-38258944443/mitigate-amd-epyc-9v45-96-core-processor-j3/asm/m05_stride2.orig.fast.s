0000000000001240 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_>:
    1240:	mov    (%rdi),%rax
    1243:	mov    0x8(%rdi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     1294 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x54>
    124c:	sar    $0x2,%rcx
    1250:	mov    (%rsi),%rdx
    1253:	mov    0x8(%rsi),%rsi
    1257:	sub    %rdx,%rsi
    125a:	sar    $0x2,%rsi
    125e:	cmp    $0x1,%rcx
    1262:	adc    $0x0,%rcx
    1266:	xor    %edi,%edi
    1268:	nopl   0x0(%rax,%rax,1)
    1270:	cmp    %rdi,%rsi
    1273:	jbe    1295 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x55>
    1275:	lea    0x1(%rdi),%r8
    1279:	cmp    %r8,%rsi
    127c:	jbe    1295 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x55>
    127e:	mov    0x4(%rdx,%rdi,4),%r8d
    1283:	add    (%rdx,%rdi,4),%r8d
    1287:	mov    %r8d,(%rax,%rdi,2)
    128b:	add    $0x2,%rdi
    128f:	dec    %rcx
    1292:	jne    1270 <_Z16kern_m05_stride2RNSt3__16vectorIiNS_9allocatorIiEEEERKS3_+0x30>
    1294:	ret
    1295:	ud2
    1297:	nopw   0x0(%rax,%rax,1)
