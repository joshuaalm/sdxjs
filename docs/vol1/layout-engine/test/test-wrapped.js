import assert from 'assert'

import {
  WrappedBlock as Block,
  WrappedCol as Col,
  WrappedRow as Row
} from '../wrapped.js'

describe('wraps blocks', () => {
  it('wraps a single unit block', async () => {
    const fixture = new Block(1, 1)
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['block', 0, 0]
    )
  })

  it('wraps a large block', async () => {
    const fixture = new Block(3, 4)
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['block', 0, 0]
    )
  })

  it('wrap a row of two blocks that fit on one row', async () => {
    const fixture = new Row(
      100,
      new Block(1, 1),
      new Block(2, 4)
    )
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['row', 0, 0, ['col', 0, 0, ['row', 0, 0, ['block', 0, -3], ['block', 1, 0]]]]
    )
  })

  it('wraps a col of two blocks', async () => {
    const fixture = new Col(
      new Block(1, 1),
      new Block(2, 4)
    )
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['col', 0, 0, ['block', 0, 0], ['block', 0, -1]]
    )
  })

  it('wraps a grid of rows of columns that all fit on their row', async () => {
    const fixture = new Col(
      new Row(
        100,
        new Block(1, 2),
        new Block(3, 4)
      ),
      new Row(
        100,
        new Block(5, 6),
        new Col(
          new Block(7, 8),
          new Block(9, 10)
        )
      )
    )
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['col', 0, 0,
        ['row', 0, 0,
          ['col', 0, 0,
            ['row', 0, 0, ['block', 0, -2], ['block', 1, 0]]]],
        ['row', 0, -4,
          ['col', 0, -4,
            ['row', 0, -4,
              ['block', 0, -16],
              ['col', 5, -4, ['block', 5, -4], ['block', 5, -12]]
            ]
          ]
        ]
      ]
    )
  })

  // <example>
  it('wrap a row of two blocks that do not fit on one row', async () => {
    const fixture = new Row(
      3,
      new Block(2, 1),
      new Block(2, 1)
    )
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['row', 0, 0,
        ['col', 0, 0,
          ['row', 0, 0,
            ['block', 0, 0]
          ],
          ['row', 0, -1,
            ['block', 0, -1]
          ]
        ]
      ]
    )
  })
  // </example>

  it('wrap multiple blocks that do not fit on one row', async () => {
    const fixture = new Row(
      3,
      new Block(2, 1),
      new Block(2, 1),
      new Block(1, 1),
      new Block(2, 1)
    )
    const wrapped = fixture.wrap()
    wrapped.place(0, 0)
    assert.deepStrictEqual(
      wrapped.report(),
      ['row', 0, 0,
        ['col', 0, 0,
          ['row', 0, 0,
            ['block', 0, 0]
          ],
          ['row', 0, -1,
            ['block', 0, -1],
            ['block', 2, -1]
          ],
          ['row', 0, -2,
            ['block', 0, -2]
          ]
        ]
      ]
    )
  })
})
