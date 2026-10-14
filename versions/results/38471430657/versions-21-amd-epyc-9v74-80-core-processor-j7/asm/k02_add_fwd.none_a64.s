0000000000001240 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_>:
    1240:	mov    (%rsi),%rax
    1243:	mov    0x8(%rsi),%rcx
    1247:	sub    %rax,%rcx
    124a:	je     13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    1250:	sar    $0x2,%rcx
    1254:	mov    (%rdx),%rdx
    1257:	mov    (%rdi),%rsi
    125a:	cmp    $0xc,%rcx
    125e:	jb     1285 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x45>
    1260:	mov    %rsi,%rdi
    1263:	sub    %rax,%rdi
    1266:	cmp    $0x20,%rdi
    126a:	setb   %dil
    126e:	mov    %rsi,%r8
    1271:	sub    %rdx,%r8
    1274:	cmp    $0x20,%r8
    1278:	setb   %r8b
    127c:	or     %dil,%r8b
    127f:	je     1344 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x104>
    1285:	xor    %edi,%edi
    1287:	mov    %rcx,%r9
    128a:	mov    %rdi,%r8
    128d:	and    $0x3,%r9
    1291:	je     12d4 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x94>
    1293:	mov    %rdi,%r8
    1296:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12a5:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12b4:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    12c0:	mov    (%rdx,%r8,4),%r10d
    12c4:	add    (%rax,%r8,4),%r10d
    12c8:	mov    %r10d,(%rsi,%r8,4)
    12cc:	inc    %r8
    12cf:	dec    %r9
    12d2:	jne    12c0 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x80>
    12d4:	sub    %rcx,%rdi
    12d7:	cmp    $0xfffffffffffffffc,%rdi
    12db:	ja     13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    12e1:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f0:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ff:	nop
    1300:	mov    (%rdx,%r8,4),%edi
    1304:	add    (%rax,%r8,4),%edi
    1308:	mov    %edi,(%rsi,%r8,4)
    130c:	mov    0x4(%rdx,%r8,4),%edi
    1311:	add    0x4(%rax,%r8,4),%edi
    1316:	mov    %edi,0x4(%rsi,%r8,4)
    131b:	mov    0x8(%rdx,%r8,4),%edi
    1320:	add    0x8(%rax,%r8,4),%edi
    1325:	mov    %edi,0x8(%rsi,%r8,4)
    132a:	mov    0xc(%rdx,%r8,4),%edi
    132f:	add    0xc(%rax,%r8,4),%edi
    1334:	mov    %edi,0xc(%rsi,%r8,4)
    1339:	add    $0x4,%r8
    133d:	cmp    %r8,%rcx
    1340:	jne    1300 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0xc0>
    1342:	jmp    13c1 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x181>
    1344:	mov    %rcx,%rdi
    1347:	and    $0xfffffffffffffff8,%rdi
    134b:	xor    %r8d,%r8d
    134e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    135d:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    136c:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    137b:	nopl   0x0(%rax,%rax,1)
    1380:	movdqu (%rax,%r8,4),%xmm0
    1386:	movdqu 0x10(%rax,%r8,4),%xmm1
    138d:	movdqu (%rdx,%r8,4),%xmm2
    1393:	paddd  %xmm0,%xmm2
    1397:	movdqu 0x10(%rdx,%r8,4),%xmm0
    139e:	paddd  %xmm1,%xmm0
    13a2:	movdqu %xmm2,(%rsi,%r8,4)
    13a8:	movdqu %xmm0,0x10(%rsi,%r8,4)
    13af:	add    $0x8,%r8
    13b3:	cmp    %r8,%rdi
    13b6:	jne    1380 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x140>
    13b8:	cmp    %rdi,%rcx
    13bb:	jne    1287 <_Z16kern_k02_add_fwdRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_S6_+0x47>
    13c1:	ret
    13c2:	data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
