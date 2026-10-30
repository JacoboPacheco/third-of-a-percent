0000000000001200 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
    1200:	test   %edx,%edx
    1202:	jle    1328 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x128>
    1208:	mov    (%rsi),%rax
    120b:	mov    (%rdi),%rsi
    120e:	movslq %ecx,%rdi
    1211:	mov    %edx,%ecx
    1213:	lea    (%rsi,%rdi,4),%r8
    1217:	cmp    $0xc,%edx
    121a:	jb     122c <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x2c>
    121c:	mov    %r8,%rdx
    121f:	sub    %rax,%rdx
    1222:	cmp    $0x20,%rdx
    1226:	jae    12b1 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xb1>
    122c:	xor    %edx,%edx
    122e:	mov    %rcx,%r10
    1231:	mov    %rdx,%r9
    1234:	and    $0x3,%r10
    1238:	je     1250 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x50>
    123a:	mov    %rdx,%r9
    123d:	nopl   (%rax)
    1240:	mov    (%rax,%r9,4),%r11d
    1244:	mov    %r11d,(%r8,%r9,4)
    1248:	inc    %r9
    124b:	dec    %r10
    124e:	jne    1240 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x40>
    1250:	sub    %rcx,%rdx
    1253:	cmp    $0xfffffffffffffffc,%rdx
    1257:	ja     1328 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x128>
    125d:	lea    (%rsi,%rdi,4),%rdx
    1261:	add    $0xc,%rdx
    1265:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    1274:	data16 data16 cs nopw 0x0(%rax,%rax,1)
    1280:	mov    (%rax,%r9,4),%esi
    1284:	mov    %esi,-0xc(%rdx,%r9,4)
    1289:	mov    0x4(%rax,%r9,4),%esi
    128e:	mov    %esi,-0x8(%rdx,%r9,4)
    1293:	mov    0x8(%rax,%r9,4),%esi
    1298:	mov    %esi,-0x4(%rdx,%r9,4)
    129d:	mov    0xc(%rax,%r9,4),%esi
    12a2:	mov    %esi,(%rdx,%r9,4)
    12a6:	add    $0x4,%r9
    12aa:	cmp    %r9,%rcx
    12ad:	jne    1280 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x80>
    12af:	jmp    1328 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x128>
    12b1:	lea    0x0(,%rdi,4),%r9
    12b9:	mov    %ecx,%edx
    12bb:	and    $0x7ffffff8,%edx
    12c1:	add    %rsi,%r9
    12c4:	add    $0x10,%r9
    12c8:	mov    %ecx,%r10d
    12cb:	shr    $0x3,%r10d
    12cf:	and    $0xfffffff,%r10d
    12d6:	shl    $0x5,%r10
    12da:	xor    %r11d,%r11d
    12dd:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12ec:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12fb:	nopl   0x0(%rax,%rax,1)
    1300:	movups (%rax,%r11,1),%xmm0
    1305:	movups 0x10(%rax,%r11,1),%xmm1
    130b:	movups %xmm0,-0x10(%r9,%r11,1)
    1311:	movups %xmm1,(%r9,%r11,1)
    1316:	add    $0x20,%r11
    131a:	cmp    %r11,%r10
    131d:	jne    1300 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x100>
    131f:	cmp    %rcx,%rdx
    1322:	jne    122e <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x2e>
    1328:	ret
    1329:	nopl   0x0(%rax)
