0000000000001250 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE>:
    1250:	mov    (%rdi),%rcx
    1253:	mov    0x8(%rdi),%rax
    1257:	sub    %rcx,%rax
    125a:	je     1277 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x27>
    125c:	sar    $0x2,%rax
    1260:	cmp    $0x1,%rax
    1264:	mov    %rax,%rdx
    1267:	adc    $0x0,%rdx
    126b:	cmp    $0x4,%rax
    126f:	jae    127b <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x2b>
    1271:	xor    %esi,%esi
    1273:	xor    %eax,%eax
    1275:	jmp    12de <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x8e>
    1277:	xor    %eax,%eax
    1279:	jmp    12d8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    127b:	mov    %rdx,%rsi
    127e:	and    $0xfffffffffffffffc,%rsi
    1282:	pxor   %xmm0,%xmm0
    1286:	xor    %eax,%eax
    1288:	pxor   %xmm1,%xmm1
    128c:	nopl   0x0(%rax)
    1290:	movq   (%rcx,%rax,4),%xmm2
    1295:	movq   0x8(%rcx,%rax,4),%xmm3
    129b:	pxor   %xmm4,%xmm4
    129f:	pcmpgtd %xmm2,%xmm4
    12a3:	punpckldq %xmm4,%xmm2
    12a7:	paddq  %xmm2,%xmm0
    12ab:	pxor   %xmm2,%xmm2
    12af:	pcmpgtd %xmm3,%xmm2
    12b3:	punpckldq %xmm2,%xmm3
    12b7:	paddq  %xmm3,%xmm1
    12bb:	add    $0x4,%rax
    12bf:	cmp    %rax,%rsi
    12c2:	jne    1290 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x40>
    12c4:	paddq  %xmm0,%xmm1
    12c8:	pshufd $0xee,%xmm1,%xmm0
    12cd:	paddq  %xmm1,%xmm0
    12d1:	movq   %xmm0,%rax
    12d6:	jmp    12d9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12d8:	ret
    12d9:	cmp    %rsi,%rdx
    12dc:	je     12d8 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x88>
    12de:	movslq (%rcx,%rsi,4),%rdi
    12e2:	add    %rdi,%rax
    12e5:	inc    %rsi
    12e8:	jmp    12d9 <_Z16kern_k01_sum_fwdRKNSt3__16vectorIiNS_9allocatorIiEEEE+0x89>
    12ea:	nopw   0x0(%rax,%rax,1)
