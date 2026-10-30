0000000000001240 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
    1240:	test   %rsi,%rsi
    1243:	je     1257 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x17>
    1245:	mov    (%rdi),%rax
    1248:	cmp    $0x4,%rsi
    124c:	jae    125d <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x1d>
    124e:	xor    %ecx,%ecx
    1250:	xor    %edi,%edi
    1252:	jmp    1300 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0xc0>
    1257:	xor    %edi,%edi
    1259:	mov    %rdi,(%rdx)
    125c:	ret
    125d:	mov    %rsi,%rcx
    1260:	and    $0xfffffffffffffffc,%rcx
    1264:	pxor   %xmm0,%xmm0
    1268:	xor    %edi,%edi
    126a:	pxor   %xmm1,%xmm1
    126e:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    127d:	nopl   (%rax)
    1280:	movq   (%rax,%rdi,4),%xmm2
    1285:	movq   0x8(%rax,%rdi,4),%xmm3
    128b:	pxor   %xmm4,%xmm4
    128f:	pcmpgtd %xmm2,%xmm4
    1293:	punpckldq %xmm4,%xmm2
    1297:	paddq  %xmm2,%xmm0
    129b:	pxor   %xmm2,%xmm2
    129f:	pcmpgtd %xmm3,%xmm2
    12a3:	punpckldq %xmm2,%xmm3
    12a7:	paddq  %xmm3,%xmm1
    12ab:	add    $0x4,%rdi
    12af:	cmp    %rdi,%rcx
    12b2:	jne    1280 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x40>
    12b4:	paddq  %xmm0,%xmm1
    12b8:	pshufd $0xee,%xmm1,%xmm0
    12bd:	paddq  %xmm1,%xmm0
    12c1:	movq   %xmm0,%rdi
    12c6:	cmp    %rsi,%rcx
    12c9:	je     130f <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0xcf>
    12cb:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12da:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12e9:	data16 data16 data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
    12f8:	nopl   0x0(%rax,%rax,1)
    1300:	movslq (%rax,%rcx,4),%r8
    1304:	add    %r8,%rdi
    1307:	inc    %rcx
    130a:	cmp    %rcx,%rsi
    130d:	jne    1300 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0xc0>
    130f:	mov    %rdi,(%rdx)
    1312:	ret
    1313:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
