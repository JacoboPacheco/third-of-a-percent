0000000000001220 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl>:
    1220:	test   %rsi,%rsi
    1223:	je     1234 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x14>
    1225:	mov    (%rdi),%rax
    1228:	cmp    $0x4,%rsi
    122c:	jae    123a <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x1a>
    122e:	xor    %ecx,%ecx
    1230:	xor    %edi,%edi
    1232:	jmp    12a0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x80>
    1234:	xor    %edi,%edi
    1236:	mov    %rdi,(%rdx)
    1239:	ret
    123a:	mov    %rsi,%rcx
    123d:	and    $0xfffffffffffffffc,%rcx
    1241:	pxor   %xmm0,%xmm0
    1245:	xor    %edi,%edi
    1247:	pxor   %xmm1,%xmm1
    124b:	nopl   0x0(%rax,%rax,1)
    1250:	movq   (%rax,%rdi,4),%xmm2
    1255:	movq   0x8(%rax,%rdi,4),%xmm3
    125b:	pxor   %xmm4,%xmm4
    125f:	pcmpgtd %xmm2,%xmm4
    1263:	punpckldq %xmm4,%xmm2
    1267:	paddq  %xmm2,%xmm0
    126b:	pxor   %xmm2,%xmm2
    126f:	pcmpgtd %xmm3,%xmm2
    1273:	punpckldq %xmm2,%xmm3
    1277:	paddq  %xmm3,%xmm1
    127b:	add    $0x4,%rdi
    127f:	cmp    %rdi,%rcx
    1282:	jne    1250 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x30>
    1284:	paddq  %xmm0,%xmm1
    1288:	pshufd $0xee,%xmm1,%xmm0
    128d:	paddq  %xmm1,%xmm0
    1291:	movq   %xmm0,%rdi
    1296:	cmp    %rsi,%rcx
    1299:	je     12af <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x8f>
    129b:	nopl   0x0(%rax,%rax,1)
    12a0:	movslq (%rax,%rcx,4),%r8
    12a4:	add    %r8,%rdi
    12a7:	inc    %rcx
    12aa:	cmp    %rcx,%rsi
    12ad:	jne    12a0 <_Z14kern_t02_sum_nRKNSt3__16vectorIiNS_9allocatorIiEEEEmPl+0x80>
    12af:	mov    %rdi,(%rdx)
    12b2:	ret
    12b3:	data16 data16 data16 cs nopw 0x0(%rax,%rax,1)
