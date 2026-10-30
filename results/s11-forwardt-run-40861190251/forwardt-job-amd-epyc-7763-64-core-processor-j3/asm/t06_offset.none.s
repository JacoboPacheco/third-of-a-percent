00000000000011e0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii>:
    11e0:	test   %edx,%edx
    11e2:	jle    12d8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xf8>
    11e8:	mov    (%rsi),%rax
    11eb:	mov    (%rdi),%rsi
    11ee:	movslq %ecx,%rdi
    11f1:	mov    %edx,%ecx
    11f3:	lea    (%rsi,%rdi,4),%r8
    11f7:	cmp    $0xc,%edx
    11fa:	jb     1208 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x28>
    11fc:	mov    %r8,%rdx
    11ff:	sub    %rax,%rdx
    1202:	cmp    $0x20,%rdx
    1206:	jae    1281 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xa1>
    1208:	xor    %edx,%edx
    120a:	mov    %rcx,%r10
    120d:	mov    %rdx,%r9
    1210:	and    $0x3,%r10
    1214:	je     1230 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x50>
    1216:	mov    %rdx,%r9
    1219:	nopl   0x0(%rax)
    1220:	mov    (%rax,%r9,4),%r11d
    1224:	mov    %r11d,(%r8,%r9,4)
    1228:	inc    %r9
    122b:	dec    %r10
    122e:	jne    1220 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x40>
    1230:	sub    %rcx,%rdx
    1233:	cmp    $0xfffffffffffffffc,%rdx
    1237:	ja     12d8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xf8>
    123d:	lea    (%rsi,%rdi,4),%rdx
    1241:	add    $0xc,%rdx
    1245:	data16 cs nopw 0x0(%rax,%rax,1)
    1250:	mov    (%rax,%r9,4),%esi
    1254:	mov    %esi,-0xc(%rdx,%r9,4)
    1259:	mov    0x4(%rax,%r9,4),%esi
    125e:	mov    %esi,-0x8(%rdx,%r9,4)
    1263:	mov    0x8(%rax,%r9,4),%esi
    1268:	mov    %esi,-0x4(%rdx,%r9,4)
    126d:	mov    0xc(%rax,%r9,4),%esi
    1272:	mov    %esi,(%rdx,%r9,4)
    1276:	add    $0x4,%r9
    127a:	cmp    %r9,%rcx
    127d:	jne    1250 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x70>
    127f:	jmp    12d8 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xf8>
    1281:	lea    0x0(,%rdi,4),%r9
    1289:	mov    %ecx,%edx
    128b:	and    $0x7ffffff8,%edx
    1291:	add    %rsi,%r9
    1294:	add    $0x10,%r9
    1298:	mov    %ecx,%r10d
    129b:	shr    $0x3,%r10d
    129f:	and    $0xfffffff,%r10d
    12a6:	shl    $0x5,%r10
    12aa:	xor    %r11d,%r11d
    12ad:	nopl   (%rax)
    12b0:	movups (%rax,%r11,1),%xmm0
    12b5:	movups 0x10(%rax,%r11,1),%xmm1
    12bb:	movups %xmm0,-0x10(%r9,%r11,1)
    12c1:	movups %xmm1,(%r9,%r11,1)
    12c6:	add    $0x20,%r11
    12ca:	cmp    %r11,%r10
    12cd:	jne    12b0 <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0xd0>
    12cf:	cmp    %rcx,%rdx
    12d2:	jne    120a <_Z15kern_t06_offsetRNSt3__16vectorIiNS_9allocatorIiEEEERKS3_ii+0x2a>
    12d8:	ret
    12d9:	nopl   0x0(%rax)
