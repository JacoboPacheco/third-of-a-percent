0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rcx
    1223:	mov    0x8(%rsi),%r8
    1227:	sub    %rcx,%r8
    122a:	je     12c4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa4>
    1230:	sar    $0x2,%r8
    1234:	mov    (%rdx),%rdx
    1237:	mov    (%rdi),%rsi
    123a:	mov    %r8d,%eax
    123d:	and    $0x3,%eax
    1240:	cmp    $0x4,%r8
    1244:	jae    124a <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x2a>
    1246:	xor    %edi,%edi
    1248:	jmp    1292 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x72>
    124a:	and    $0xfffffffffffffffc,%r8
    124e:	xor    %edi,%edi
    1250:	mov    (%rdx,%rdi,4),%r9d
    1254:	add    (%rcx,%rdi,4),%r9d
    1258:	mov    %r9d,(%rsi,%rdi,4)
    125c:	mov    0x4(%rdx,%rdi,4),%r9d
    1261:	add    0x4(%rcx,%rdi,4),%r9d
    1266:	mov    %r9d,0x4(%rsi,%rdi,4)
    126b:	mov    0x8(%rdx,%rdi,4),%r9d
    1270:	add    0x8(%rcx,%rdi,4),%r9d
    1275:	mov    %r9d,0x8(%rsi,%rdi,4)
    127a:	mov    0xc(%rdx,%rdi,4),%r9d
    127f:	add    0xc(%rcx,%rdi,4),%r9d
    1284:	mov    %r9d,0xc(%rsi,%rdi,4)
    1289:	add    $0x4,%rdi
    128d:	cmp    %rdi,%r8
    1290:	jne    1250 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x30>
    1292:	test   %rax,%rax
    1295:	je     12c4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xa4>
    1297:	lea    (%rsi,%rdi,4),%rsi
    129b:	lea    (%rdx,%rdi,4),%rdx
    129f:	lea    (%rcx,%rdi,4),%rcx
    12a3:	xor    %edi,%edi
    12a5:	data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	mov    (%rdx,%rdi,4),%r8d
    12b4:	add    (%rcx,%rdi,4),%r8d
    12b8:	mov    %r8d,(%rsi,%rdi,4)
    12bc:	inc    %rdi
    12bf:	cmp    %rdi,%rax
    12c2:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12c4:	ret
    12c5:	data16 cs nopw 0x0(%rax,%rax,1)
