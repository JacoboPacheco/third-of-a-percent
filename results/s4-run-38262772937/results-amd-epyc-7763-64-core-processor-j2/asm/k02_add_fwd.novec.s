0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%r9
    1227:	sub    %rax,%r9
    122a:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xb4>
    1230:	sar    $0x2,%r9
    1234:	mov    (%rdx),%rdx
    1237:	cmp    $0x1,%r9
    123b:	mov    %r9,%r8
    123e:	adc    $0x0,%r8
    1242:	mov    (%rdi),%rsi
    1245:	mov    %r8d,%ecx
    1248:	and    $0x3,%ecx
    124b:	cmp    $0x4,%r9
    124f:	jae    1255 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x35>
    1251:	xor    %edi,%edi
    1253:	jmp    12a2 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x82>
    1255:	and    $0xfffffffffffffffc,%r8
    1259:	xor    %edi,%edi
    125b:	nopl   0x0(%rax,%rax,1)
    1260:	mov    (%rdx,%rdi,4),%r9d
    1264:	add    (%rax,%rdi,4),%r9d
    1268:	mov    %r9d,(%rsi,%rdi,4)
    126c:	mov    0x4(%rdx,%rdi,4),%r9d
    1271:	add    0x4(%rax,%rdi,4),%r9d
    1276:	mov    %r9d,0x4(%rsi,%rdi,4)
    127b:	mov    0x8(%rdx,%rdi,4),%r9d
    1280:	add    0x8(%rax,%rdi,4),%r9d
    1285:	mov    %r9d,0x8(%rsi,%rdi,4)
    128a:	mov    0xc(%rdx,%rdi,4),%r9d
    128f:	add    0xc(%rax,%rdi,4),%r9d
    1294:	mov    %r9d,0xc(%rsi,%rdi,4)
    1299:	add    $0x4,%rdi
    129d:	cmp    %rdi,%r8
    12a0:	jne    1260 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x40>
    12a2:	test   %rcx,%rcx
    12a5:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xb4>
    12a7:	lea    (%rsi,%rdi,4),%rsi
    12ab:	lea    (%rdx,%rdi,4),%rdx
    12af:	lea    (%rax,%rdi,4),%rax
    12b3:	xor    %edi,%edi
    12b5:	data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    (%rdx,%rdi,4),%r8d
    12c4:	add    (%rax,%rdi,4),%r8d
    12c8:	mov    %r8d,(%rsi,%rdi,4)
    12cc:	inc    %rdi
    12cf:	cmp    %rdi,%rcx
    12d2:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa0>
    12d4:	ret
    12d5:	data16 cs nopw 0x0(%rax,%rax,1)
