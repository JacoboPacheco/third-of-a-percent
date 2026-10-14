0000000000001220 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1220:	mov    (%rsi),%rax
    1223:	mov    0x8(%rsi),%rcx
    1227:	sub    %rax,%rcx
    122a:	je     1341 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x121>
    1230:	sar    $0x2,%rcx
    1234:	mov    (%rdx),%rdx
    1237:	mov    (%rdi),%rsi
    123a:	cmp    $0xc,%rcx
    123e:	jb     1265 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x45>
    1240:	mov    %rsi,%rdi
    1243:	sub    %rax,%rdi
    1246:	cmp    $0x20,%rdi
    124a:	setb   %dil
    124e:	mov    %rsi,%r8
    1251:	sub    %rdx,%r8
    1254:	cmp    $0x20,%r8
    1258:	setb   %r8b
    125c:	or     %dil,%r8b
    125f:	je     12f4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xd4>
    1265:	xor    %edi,%edi
    1267:	mov    %rcx,%r9
    126a:	mov    %rdi,%r8
    126d:	and    $0x3,%r9
    1271:	je     1294 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x74>
    1273:	mov    %rdi,%r8
    1276:	cs nopw 0x0(%rax,%rax,1)
    1280:	mov    (%rdx,%r8,4),%r10d
    1284:	add    (%rax,%r8,4),%r10d
    1288:	mov    %r10d,(%rsi,%r8,4)
    128c:	inc    %r8
    128f:	dec    %r9
    1292:	jne    1280 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x60>
    1294:	sub    %rcx,%rdi
    1297:	cmp    $0xfffffffffffffffc,%rdi
    129b:	ja     1341 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x121>
    12a1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b0:	mov    (%rdx,%r8,4),%edi
    12b4:	add    (%rax,%r8,4),%edi
    12b8:	mov    %edi,(%rsi,%r8,4)
    12bc:	mov    0x4(%rdx,%r8,4),%edi
    12c1:	add    0x4(%rax,%r8,4),%edi
    12c6:	mov    %edi,0x4(%rsi,%r8,4)
    12cb:	mov    0x8(%rdx,%r8,4),%edi
    12d0:	add    0x8(%rax,%r8,4),%edi
    12d5:	mov    %edi,0x8(%rsi,%r8,4)
    12da:	mov    0xc(%rdx,%r8,4),%edi
    12df:	add    0xc(%rax,%r8,4),%edi
    12e4:	mov    %edi,0xc(%rsi,%r8,4)
    12e9:	add    $0x4,%r8
    12ed:	cmp    %r8,%rcx
    12f0:	jne    12b0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x90>
    12f2:	jmp    1341 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x121>
    12f4:	mov    %rcx,%rdi
    12f7:	and    $0xfffffffffffffff8,%rdi
    12fb:	xor    %r8d,%r8d
    12fe:	xchg   %ax,%ax
    1300:	movdqu (%rax,%r8,4),%xmm0
    1306:	movdqu 0x10(%rax,%r8,4),%xmm1
    130d:	movdqu (%rdx,%r8,4),%xmm2
    1313:	paddd  %xmm0,%xmm2
    1317:	movdqu 0x10(%rdx,%r8,4),%xmm0
    131e:	paddd  %xmm1,%xmm0
    1322:	movdqu %xmm2,(%rsi,%r8,4)
    1328:	movdqu %xmm0,0x10(%rsi,%r8,4)
    132f:	add    $0x8,%r8
    1333:	cmp    %r8,%rdi
    1336:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xe0>
    1338:	cmp    %rdi,%rcx
    133b:	jne    1267 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x47>
    1341:	ret
    1342:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
